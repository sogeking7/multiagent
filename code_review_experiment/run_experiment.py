"""Master experiment runner.

Pipeline:
  1. Load dataset/samples.json (30 snippets, 10 per category).
  2. For each sample, run all three configs. Errors are logged, not raised.
  3. Persist raw outputs after every sample so a Ctrl-C keeps partial data.
  4. After all runs, score every (sample, config) pair with the GPT-4o judge.
  5. Aggregate metrics per config and emit:
       - results/raw_outputs.json
       - results/metrics.json
       - results/comparison_table.md
       - results/qualitative_examples.md

The runner is intentionally serial across samples: the only place we use
concurrency is INSIDE Config C, where its three specialists must run in
parallel by design. Cross-sample parallelism would muddy budget accounting
and rate-limit behaviour without changing the conclusions.

Run:
  python run_experiment.py                  # full 30 samples
  python run_experiment.py --limit 3        # smoke test on 3 samples
  python run_experiment.py --skip-run       # re-judge existing raw_outputs.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_env_file() -> None:
    """Tiny .env loader so we don't add a runtime dependency.

    Reads KEY=value lines from code_review_experiment/.env if present and
    sets them in os.environ unless they are already set. Lines starting
    with `#` and blank lines are skipped. Values can be single- or
    double-quoted.
    """
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


_load_env_file()

from configs import parallel_multi, sequential_multi, single_agent  # noqa: E402
from configs._common import PRICE_IN_PER_M, PRICE_OUT_PER_M  # noqa: E402
from evaluation.judge import JudgeScore, judge_review  # noqa: E402


SAMPLES_PATH = PROJECT_ROOT / "dataset" / "samples.json"
RESULTS_DIR = PROJECT_ROOT / "results"
RAW_OUTPUTS_PATH = RESULTS_DIR / "raw_outputs.json"
METRICS_PATH = RESULTS_DIR / "metrics.json"
TABLE_PATH = RESULTS_DIR / "comparison_table.md"
QUALITATIVE_PATH = RESULTS_DIR / "qualitative_examples.md"


CONFIGS = (
    ("A_single_agent", single_agent.run),
    ("B_sequential_multi", sequential_multi.run),
    ("C_parallel_multi", parallel_multi.run),
)


# ---------------------------------------------------------------------------
# Run phase
# ---------------------------------------------------------------------------


def _load_samples() -> list[dict[str, Any]]:
    with SAMPLES_PATH.open() as f:
        return json.load(f)


def _save_raw(raw: dict[str, Any]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with RAW_OUTPUTS_PATH.open("w") as f:
        json.dump(raw, f, indent=2)


def run_phase(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Run every config on every sample and persist raw outputs."""
    raw: dict[str, Any] = {"samples": {}}
    for i, sample in enumerate(samples, start=1):
        sid = sample["id"]
        print(f"[run {i}/{len(samples)}] sample={sid} category={sample['category']}")
        sample_record: dict[str, Any] = {
            "id": sid,
            "category": sample["category"],
            "code": sample["code"],
            "known_issues": sample["known_issues"],
            "configs": {},
        }
        for name, run_fn in CONFIGS:
            t0 = time.time()
            try:
                result = run_fn(sample["code"])
                record = result.to_dict()
            except Exception:  # noqa: BLE001 — top-level safety net
                record = {
                    "config_name": name,
                    "final_output": "",
                    "error": traceback.format_exc(),
                    "total_tokens_in": 0,
                    "total_tokens_out": 0,
                    "total_tokens": 0,
                    "agent_calls": [],
                }
            record["wall_time_s"] = round(time.time() - t0, 3)
            sample_record["configs"][name] = record
            err = record.get("error")
            tokens = record.get("total_tokens", 0)
            print(
                f"    {name:22s} tokens={tokens:5d}  "
                f"time={record['wall_time_s']:.2f}s  "
                f"err={'-' if not err else err[:60]}"
            )
        raw["samples"][sid] = sample_record
        _save_raw(raw)
    return raw


# ---------------------------------------------------------------------------
# Judge phase
# ---------------------------------------------------------------------------


def judge_phase(raw: dict[str, Any]) -> dict[str, Any]:
    """Score every config output. Mutates `raw` in place and persists."""
    client = OpenAI()
    samples = raw["samples"]
    total = len(samples) * len(CONFIGS)
    done = 0
    for sid, sample_record in samples.items():
        for name, _ in CONFIGS:
            done += 1
            cfg = sample_record["configs"][name]
            if "judge" in cfg:
                # Already judged (e.g. resuming a previous run).
                continue
            score: JudgeScore = judge_review(
                client,
                code=sample_record["code"],
                known_issues=sample_record["known_issues"],
                review=cfg.get("final_output", ""),
            )
            cfg["judge"] = score.to_dict()
            status = "ok" if not score.parse_error else f"parse_err: {score.parse_error}"
            print(
                f"[judge {done}/{total}] sample={sid} config={name}  "
                f"recall={score.recall_score:.2f} precision={score.precision_score:.2f} "
                f"redund={score.redundancy_count} rel={score.relevance_score}  {status}"
            )
        _save_raw(raw)
    return raw


# ---------------------------------------------------------------------------
# Aggregation phase
# ---------------------------------------------------------------------------


def _agg_one(values: list[float]) -> float | None:
    return round(mean(values), 4) if values else None


def aggregate(raw: dict[str, Any]) -> dict[str, Any]:
    """Compute per-config and per-category aggregate metrics."""
    per_config_metrics: dict[str, dict[str, Any]] = {}
    per_config_cat: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )

    for cfg_name, _ in CONFIGS:
        recall, precision, redundancy, relevance = [], [], [], []
        tokens_in, tokens_out, tokens_total = [], [], []
        run_errors = 0
        judge_errors = 0
        for sid, rec in raw["samples"].items():
            cfg = rec["configs"][cfg_name]
            if cfg.get("error"):
                run_errors += 1
            tokens_in.append(cfg.get("total_tokens_in", 0))
            tokens_out.append(cfg.get("total_tokens_out", 0))
            tokens_total.append(cfg.get("total_tokens", 0))

            judge = cfg.get("judge", {})
            if judge.get("parse_error"):
                judge_errors += 1
                continue
            r = judge.get("recall_score")
            p = judge.get("precision_score")
            d = judge.get("redundancy_count")
            v = judge.get("relevance_score")
            if r is None or p is None or d is None or v is None:
                judge_errors += 1
                continue
            recall.append(r)
            precision.append(p)
            redundancy.append(d)
            relevance.append(v)

            cat = rec["category"]
            per_config_cat[cfg_name][cat]["recall"].append(r)
            per_config_cat[cfg_name][cat]["precision"].append(p)

        total_in = sum(tokens_in)
        total_out = sum(tokens_out)
        cost_in = total_in / 1_000_000 * PRICE_IN_PER_M
        cost_out = total_out / 1_000_000 * PRICE_OUT_PER_M
        per_config_metrics[cfg_name] = {
            "mean_recall": _agg_one(recall),
            "mean_precision": _agg_one(precision),
            "mean_redundancy": _agg_one(redundancy),
            "mean_relevance": _agg_one(relevance),
            "mean_tokens_in": _agg_one(tokens_in),
            "mean_tokens_out": _agg_one(tokens_out),
            "mean_tokens_total": _agg_one(tokens_total),
            "total_tokens_in": total_in,
            "total_tokens_out": total_out,
            "estimated_cost_usd": round(cost_in + cost_out, 6),
            "n_run_errors": run_errors,
            "n_judge_errors": judge_errors,
            "n_scored": len(recall),
        }

    per_category: dict[str, dict[str, dict[str, float | None]]] = {}
    for cfg_name, by_cat in per_config_cat.items():
        per_category[cfg_name] = {}
        for cat, metrics in by_cat.items():
            per_category[cfg_name][cat] = {
                "mean_recall": _agg_one(metrics["recall"]),
                "mean_precision": _agg_one(metrics["precision"]),
                "n": len(metrics["recall"]),
            }

    return {
        "per_config": per_config_metrics,
        "per_config_per_category": per_category,
    }


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _fmt(v: float | int | None, *, pct: bool = False, digits: int = 3) -> str:
    if v is None:
        return "—"
    if pct:
        return f"{v * 100:.1f}%"
    if isinstance(v, int):
        return str(v)
    return f"{v:.{digits}f}"


def build_comparison_table(metrics: dict[str, Any]) -> str:
    pc = metrics["per_config"]
    A, B, C = pc["A_single_agent"], pc["B_sequential_multi"], pc["C_parallel_multi"]
    lines = [
        "# Comparison Table",
        "",
        "Token budget: 600 output tokens per sample across all configurations.",
        "Costs are for agent calls only (gpt-4o-mini) and exclude judge tokens.",
        "",
        "| Metric              | Config A (Single) | Config B (Sequential) | Config C (Parallel) |",
        "|---------------------|-------------------|-----------------------|---------------------|",
        f"| Mean Recall         | {_fmt(A['mean_recall'], pct=True)} | {_fmt(B['mean_recall'], pct=True)} | {_fmt(C['mean_recall'], pct=True)} |",
        f"| Mean Precision      | {_fmt(A['mean_precision'], pct=True)} | {_fmt(B['mean_precision'], pct=True)} | {_fmt(C['mean_precision'], pct=True)} |",
        f"| Mean Redundancy     | {_fmt(A['mean_redundancy'])} | {_fmt(B['mean_redundancy'])} | {_fmt(C['mean_redundancy'])} |",
        f"| Mean Relevance      | {_fmt(A['mean_relevance'])} | {_fmt(B['mean_relevance'])} | {_fmt(C['mean_relevance'])} |",
        f"| Mean Tokens Used    | {_fmt(A['mean_tokens_total'], digits=1)} | {_fmt(B['mean_tokens_total'], digits=1)} | {_fmt(C['mean_tokens_total'], digits=1)} |",
        f"| Est. Cost per 30    | ${A['estimated_cost_usd']:.4f} | ${B['estimated_cost_usd']:.4f} | ${C['estimated_cost_usd']:.4f} |",
        "",
        "## Per-category recall (defect-finding by issue type)",
        "",
        "| Category | Config A | Config B | Config C |",
        "|----------|----------|----------|----------|",
    ]
    for cat in ("logic", "security", "style"):
        a = metrics["per_config_per_category"]["A_single_agent"].get(cat, {}).get("mean_recall")
        b = metrics["per_config_per_category"]["B_sequential_multi"].get(cat, {}).get("mean_recall")
        c = metrics["per_config_per_category"]["C_parallel_multi"].get(cat, {}).get("mean_recall")
        lines.append(
            f"| {cat:8s} | {_fmt(a, pct=True)} | {_fmt(b, pct=True)} | {_fmt(c, pct=True)} |"
        )

    lines += [
        "",
        "## Run / judge errors",
        "",
        "| Config | Run errors | Judge errors | Samples scored |",
        "|--------|-----------:|-------------:|---------------:|",
    ]
    for name, _ in CONFIGS:
        m = pc[name]
        lines.append(
            f"| {name} | {m['n_run_errors']} | {m['n_judge_errors']} | {m['n_scored']} |"
        )

    return "\n".join(lines) + "\n"


def pick_qualitative_examples(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Pick three samples: multi clearly wins, single clearly wins, tied.

    'Multi wins' = max(B_recall, C_recall) - A_recall is largest positive.
    'Single wins' = A_recall - max(B_recall, C_recall) is largest positive.
    'Tied' = smallest range across all three recall scores.
    """
    rows = []
    for sid, rec in raw["samples"].items():
        scores = {}
        ok = True
        for cfg_name, _ in CONFIGS:
            judge = rec["configs"][cfg_name].get("judge", {})
            r = judge.get("recall_score")
            if r is None or judge.get("parse_error"):
                ok = False
                break
            scores[cfg_name] = r
        if not ok:
            continue
        rows.append(
            {
                "id": sid,
                "category": rec["category"],
                "a": scores["A_single_agent"],
                "b": scores["B_sequential_multi"],
                "c": scores["C_parallel_multi"],
            }
        )

    if not rows:
        return []

    multi_win = max(rows, key=lambda r: max(r["b"], r["c"]) - r["a"])
    single_win = max(rows, key=lambda r: r["a"] - max(r["b"], r["c"]))
    tied = min(rows, key=lambda r: max(r["a"], r["b"], r["c"]) - min(r["a"], r["b"], r["c"]))

    picks = []
    for label, row in (
        ("Multi-agent clearly won", multi_win),
        ("Single-agent clearly won", single_win),
        ("All configs tied", tied),
    ):
        picks.append({"label": label, **row})
    return picks


def build_qualitative_doc(raw: dict[str, Any], picks: list[dict[str, Any]]) -> str:
    parts = ["# Qualitative Examples", ""]
    if not picks:
        parts.append("_No successfully-judged samples; nothing to compare._\n")
        return "\n".join(parts)
    for pick in picks:
        rec = raw["samples"][pick["id"]]
        parts.append(
            f"## {pick['label']} — sample `{pick['id']}` "
            f"({rec['category']})"
        )
        parts.append("")
        parts.append(
            f"Recall by config: "
            f"A={pick['a']:.2f}, B={pick['b']:.2f}, C={pick['c']:.2f}"
        )
        parts.append("")
        parts.append("### Code under review")
        parts.append("```python")
        parts.append(rec["code"])
        parts.append("```")
        parts.append("")
        parts.append("### Canonical known issues")
        for iss in rec["known_issues"]:
            parts.append(f"- {iss}")
        parts.append("")
        for cfg_name, label in (
            ("A_single_agent", "Config A — Single Agent"),
            ("B_sequential_multi", "Config B — Sequential Multi-Agent"),
            ("C_parallel_multi", "Config C — Parallel Multi-Agent"),
        ):
            cfg = rec["configs"][cfg_name]
            parts.append(f"### {label}")
            parts.append("```")
            parts.append((cfg.get("final_output") or "(empty)").strip())
            parts.append("```")
            judge = cfg.get("judge", {})
            parts.append(
                f"_Judge:_ recall={judge.get('recall_score'):.2f}, "
                f"precision={judge.get('precision_score'):.2f}, "
                f"redundancy={judge.get('redundancy_count')}, "
                f"relevance={judge.get('relevance_score')}. "
                f"{judge.get('reasoning', '')}"
            )
            parts.append("")
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Run on only the first N samples (smoke test).",
    )
    parser.add_argument(
        "--skip-run", action="store_true",
        help="Skip the run phase and judge existing raw_outputs.json.",
    )
    parser.add_argument(
        "--skip-judge", action="store_true",
        help="Skip the judge phase (e.g. just collect outputs).",
    )
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "ERROR: OPENAI_API_KEY is not set. Set it in your environment "
            "before running.",
            file=sys.stderr,
        )
        return 2

    if args.skip_run:
        if not RAW_OUTPUTS_PATH.exists():
            print("ERROR: --skip-run requires existing raw_outputs.json", file=sys.stderr)
            return 2
        with RAW_OUTPUTS_PATH.open() as f:
            raw = json.load(f)
    else:
        samples = _load_samples()
        if args.limit:
            samples = samples[: args.limit]
        raw = run_phase(samples)

    if not args.skip_judge:
        raw = judge_phase(raw)

    metrics = aggregate(raw)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    table = build_comparison_table(metrics)
    TABLE_PATH.write_text(table)
    print("\n" + table)

    picks = pick_qualitative_examples(raw)
    QUALITATIVE_PATH.write_text(build_qualitative_doc(raw, picks))
    print(f"Qualitative examples written to {QUALITATIVE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
