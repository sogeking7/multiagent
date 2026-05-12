# Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review

A controlled comparison of three LLM-based code-review configurations under
equal output-token budgets. The artefacts here — code, dataset, raw outputs,
and metrics — are intended to feed directly into the corresponding paper's
Methodology and Results sections.

---

## 1. Experimental control: equal output-token budget

The central confound when comparing single-agent and multi-agent LLM systems
is **inference budget**. A multi-agent system that performs better than a
single agent typically also issues more LLM calls and emits more total
tokens — so any observed performance gap may be attributable to compute,
not architecture. Without controlling for budget, the comparison answers
"is more inference better?" rather than the architectural question we care
about: *given a fixed inference budget, does role specialization help?*

We therefore fix the per-sample output-token budget at **600 tokens** across
all three configurations and enforce it with `max_tokens` on every API call:

| Configuration               | Budget allocation                                                   |
|-----------------------------|---------------------------------------------------------------------|
| A — Single agent            | 600 tokens, one call                                                |
| B — Sequential multi-agent  | 200 tokens × 3 specialists (logic, security, style), run in order  |
| C — Parallel multi-agent    | 150 × 3 specialists + 150 for an aggregator                         |

Each call's actual `usage.completion_tokens` and `usage.prompt_tokens` are
logged from the API response, so we can verify after the fact that no
configuration silently exceeded its budget. Note that **input** tokens are
not equalised: by design, Config B and Config C have higher input cost
because later agents read earlier outputs (B) or all specialists' outputs
(C aggregator). Discussion of this asymmetry belongs in the paper; we
report mean input, output, and total tokens separately so readers can
draw their own conclusions.

## 2. The three configurations and the hypotheses they isolate

Each configuration corresponds to a distinct architectural hypothesis about
where the gains from LLM-based review come from.

**Config A — Single agent.** A single "general" code reviewer with the full
600-token budget. This is the baseline: it tests whether role specialization
adds value over a competent generalist with equal budget.

**Config B — Sequential multi-agent.** Three role-specialised reviewers
(logic → security → style) run in order, each seeing the original code plus
all earlier reviews and explicitly instructed not to duplicate prior
findings. This tests two combined effects: (i) role specialization, and
(ii) sequential context-building, where later agents can refine or extend
earlier analysis. The hypothesis is that focused-role prompts produce
denser, less hedged reviews per role than a generalist would, and that
deduplication-aware context produces less redundant final output.

**Config C — Parallel multi-agent with aggregator.** Three role-specialised
reviewers run independently (no cross-visibility) and a fourth aggregator
agent merges their outputs into a unified deduplicated list. This isolates
**pure role specialization** — the specialists cannot benefit from one
another's framing — and tests whether an explicit aggregation step recovers
the deduplication benefit that sequential context provides "for free."

Comparing B and C therefore isolates the effect of sequential context-sharing
versus a dedicated aggregation pass, holding role-specialisation constant.

## 3. Model selection

We use `gpt-4o-mini` for all agent roles in all three configurations and
`gpt-4o` (the larger sibling) as the judge.

**Why `gpt-4o-mini` for agents.** The mini model is the realistic
production-cost regime for code review at scale (≈ $0.15/1M input + $0.60/1M
output as of 2025). Using a frontier model for the agents would inflate
absolute scores across the board and risk a ceiling effect that obscures
inter-configuration differences. Using the cheaper model makes any
architectural lift more visible.

**Why `gpt-4o` (not mini) for the judge.** The judge must compare three
reviews against a canonical issue list, count duplicates, and assign
calibrated scores. This is a more demanding task than producing a single
review, and pilot work using the mini model as judge showed inconsistent
clamping of the [0,1] scores and frequent invalid-JSON output. Using the
larger model and a JSON-only response format mitigates both problems. The
judge is identical across configurations, so any residual judge bias affects
all three equally.

**Temperature.** Agents run at `temperature=0.2` — low enough to be largely
deterministic but non-zero so the three Config-C specialists do not produce
identical text that would inflate the redundancy metric. The judge runs at
`temperature=0.0`.

## 4. Dataset construction and known biases

`dataset/samples.json` contains 30 Python snippets of 10–30 lines, stratified
into three categories of 10 samples each:

- **Logic bugs** (L1–L10): off-by-one errors, mutable default args, inverted
  conditionals, closure capture, integer division, missing base cases,
  float-equality on money, naive CSV splitting, missing empty-input handling.
- **Security issues** (S1–S10): SQL injection, hardcoded credentials,
  pickle deserialization, path traversal, weak RNG for tokens, command
  injection, XSS, MD5 password hashing, SSRF, `eval()` on user input.
- **Style / maintainability** (ST1–ST10): deep nesting, missing error
  handling, single-letter names, magic numbers, missing input validation,
  DRY violations, single-responsibility violations, bare `except`, mutable
  module-level state, inconsistent return types.

Each snippet was written by hand to be **realistic** — resembling code a
working engineer might actually commit — and **subtle**, meaning a non-expert
reviewer could plausibly miss at least one issue. Snippets are seeded with a
deliberate, enumerated list of known issues in `known_issues`. Several
snippets contain multiple known issues (e.g. S8 has both MD5 hashing and
non-constant-time comparison; ST5 has both validation and atomicity issues),
which makes recall scoring more discriminating than a one-issue-per-snippet
design would.

**Known dataset biases.** First, the canonical `known_issues` list reflects
*our* judgement of what is a real defect; an aggressive reviewer can correctly
flag issues we did not enumerate, which depresses the precision metric —
hence the judge is explicitly told that precision measures real-defect
validity, not appearance in the canonical list. Second, all samples are
short, single-function Python — results may not transfer to long-context
multi-file review. Third, the category split (logic / security / style) maps
cleanly onto the three specialist roles in Configs B and C, which is the most
favourable design for role-specialisation; a paper using this dataset should
caveat that real-world reviews mix categories within a single review surface.
Fourth, snippets were written knowing that LLMs would later be asked to find
the planted issues — this introduces selection bias toward LLM-detectable
bugs (e.g. we did not plant deep numerical-stability issues or concurrency
races that no static review would catch).

## 5. Limitations of the experimental design

- **N=30.** Small enough that observed mean differences across configurations
  should be reported with confidence intervals / a paired test (e.g. paired
  bootstrap or Wilcoxon signed-rank) rather than treated as significant on
  their own. The judge metrics are saved per-sample in `raw_outputs.json` so
  any such test can be run post-hoc.
- **Single language (Python).** Findings may not generalise to languages
  with different idioms, error-handling cultures, or security models (e.g.
  Rust, Go, JavaScript).
- **Single judge model.** GPT-4o judging GPT-4o-mini outputs is an
  in-family evaluation; cross-family judging (e.g. Claude) would be a
  stronger robustness check.
- **Single token budget.** 600 tokens is one operating point. Real systems
  may operate at substantially higher or lower budgets where the relative
  ranking may change. A budget-sweep experiment is left to future work.
- **Static prompts.** None of the configurations use tools, retrieval, or
  iterative refinement. The conclusions speak only to the "single forward
  pass per agent" regime.
- **Judge subjectivity.** Recall and precision are graded by an LLM, not by
  string match. We mitigate by giving the judge the canonical issue list and
  by clamping scores into expected ranges, but residual judge variance is a
  fact of the design.

---

## Repository layout

```
code_review_experiment/
├── dataset/
│   ├── build_samples.py     # Generator (run once) — keeps Python strings readable
│   └── samples.json         # 30 samples committed for reproducibility
├── configs/
│   ├── _common.py           # Shared client, AgentCall/ConfigResult, model IDs
│   ├── single_agent.py      # Config A
│   ├── sequential_multi.py  # Config B
│   └── parallel_multi.py    # Config C (asyncio.gather across specialists)
├── evaluation/
│   └── judge.py             # GPT-4o-as-judge with defensive JSON parsing
├── results/
│   ├── raw_outputs.json     # Per-sample agent outputs + judge scores
│   ├── metrics.json         # Aggregated per-config and per-category metrics
│   ├── comparison_table.md  # The headline table reproduced in the paper
│   └── qualitative_examples.md  # Three case studies
├── run_experiment.py        # Master runner
└── README.md                # This file
```

## How to reproduce

```bash
# 1. Install deps (one-liner).
pip install openai

# 2. Provide an API key.
export OPENAI_API_KEY=sk-...

# 3. (Re)build the dataset if you modify build_samples.py.
python dataset/build_samples.py

# 4. Run the full experiment (~120 agent calls + ~90 judge calls).
python run_experiment.py

# Useful flags:
python run_experiment.py --limit 3        # smoke test on 3 samples
python run_experiment.py --skip-run       # re-judge an existing run
python run_experiment.py --skip-judge     # collect outputs only
```

Raw outputs are saved after every sample, so an interrupted run can be
inspected or resumed (`--skip-run` re-uses the saved outputs and only
runs the judge phase). The judge phase is also idempotent per (sample,
config) — already-scored entries are skipped on re-run.
