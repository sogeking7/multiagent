"""GPT-4o-as-judge scorer.

For each (sample, config-output) pair the judge sees:
  - the original code
  - the canonical `known_issues` list for that sample
  - the review text the config produced

and returns a JSON object with recall, precision, redundancy, and a 1-5
relevance score. The judge is told to return JSON only — we still parse
defensively in case it wraps the object in markdown fences.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

# We use the absolute import here because the judge is invoked from
# run_experiment.py with the project root on sys.path, not as part of the
# `configs` package.
import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from configs._common import JUDGE_MODEL  # noqa: E402


JUDGE_SYSTEM = (
    "You are a careful, impartial reviewer judging the quality of a code "
    "review. You will be given (a) source code, (b) a canonical list of "
    "known issues in that code, and (c) a review produced by another "
    "system.\n\n"
    "Score the review on four dimensions and return ONLY a single valid "
    "JSON object with these keys:\n"
    "  recall_score:     float in [0.0, 1.0] — fraction of canonical known "
    "issues the review identifies (a near-paraphrase counts).\n"
    "  precision_score:  float in [0.0, 1.0] — fraction of distinct issues "
    "raised by the review that are valid real problems in the code (whether "
    "or not they appear in the canonical list).\n"
    "  redundancy_count: integer >= 0 — count of duplicate or near-duplicate "
    "points within the review (e.g. the same SQL injection raised twice).\n"
    "  relevance_score:  integer in {1,2,3,4,5} — overall quality of the "
    "review as a holistic code-review artifact.\n"
    "  reasoning:        one short sentence justifying the scores.\n\n"
    "Do not output markdown, code fences, or any text outside the JSON object."
)


@dataclass
class JudgeScore:
    recall_score: float = 0.0
    precision_score: float = 0.0
    redundancy_count: int = 0
    relevance_score: int = 0
    reasoning: str = ""
    raw_response: str = ""
    parse_error: str | None = None
    tokens_in: int = 0
    tokens_out: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "recall_score": self.recall_score,
            "precision_score": self.precision_score,
            "redundancy_count": self.redundancy_count,
            "relevance_score": self.relevance_score,
            "reasoning": self.reasoning,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "parse_error": self.parse_error,
            "raw_response": self.raw_response,
        }


def _extract_json_object(text: str) -> str | None:
    """Pull the first balanced JSON object out of `text`.

    Handles three observed failure modes from the judge:
      - bare JSON (happy path)
      - JSON wrapped in ```json ... ``` fences
      - trailing commentary after the closing brace
    Returns None if no balanced object is found.
    """
    fence = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
    if fence:
        return fence.group(1)

    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_judge_response(text: str) -> tuple[dict | None, str | None]:
    candidate = _extract_json_object(text)
    if candidate is None:
        return None, "no JSON object found in response"
    try:
        return json.loads(candidate), None
    except json.JSONDecodeError as e:
        return None, f"JSONDecodeError: {e.msg}"


def _coerce_score(parsed: dict) -> JudgeScore:
    """Convert raw judge output to a typed JudgeScore, clamping ranges."""

    def _clamp_float(v: Any, lo: float, hi: float, default: float) -> float:
        try:
            x = float(v)
        except (TypeError, ValueError):
            return default
        if x < lo:
            return lo
        if x > hi:
            return hi
        return x

    def _clamp_int(v: Any, lo: int, hi: int, default: int) -> int:
        try:
            x = int(v)
        except (TypeError, ValueError):
            return default
        if x < lo:
            return lo
        if x > hi:
            return hi
        return x

    return JudgeScore(
        recall_score=_clamp_float(parsed.get("recall_score"), 0.0, 1.0, 0.0),
        precision_score=_clamp_float(
            parsed.get("precision_score"), 0.0, 1.0, 0.0
        ),
        redundancy_count=_clamp_int(
            parsed.get("redundancy_count"), 0, 1000, 0
        ),
        relevance_score=_clamp_int(parsed.get("relevance_score"), 1, 5, 1),
        reasoning=str(parsed.get("reasoning", "")).strip(),
    )


def judge_review(
    client: OpenAI,
    *,
    code: str,
    known_issues: list[str],
    review: str,
) -> JudgeScore:
    """Score a single review. Always returns a JudgeScore, even on error."""
    user_msg = (
        "ORIGINAL CODE:\n```python\n" + code + "\n```\n\n"
        "KNOWN ISSUES (canonical list, one per line):\n"
        + "\n".join(f"- {iss}" for iss in known_issues)
        + "\n\nREVIEW TO SCORE:\n" + (review.strip() or "(empty)") + "\n"
    )

    try:
        response = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=400,
            temperature=0.0,
            response_format={"type": "json_object"},
        )
    except Exception as exc:  # noqa: BLE001
        return JudgeScore(
            parse_error=f"api_error: {type(exc).__name__}: {exc}",
            raw_response="",
        )

    raw = response.choices[0].message.content or ""
    usage = response.usage
    parsed, err = _parse_judge_response(raw)
    if parsed is None:
        return JudgeScore(
            parse_error=err,
            raw_response=raw,
            tokens_in=usage.prompt_tokens if usage else 0,
            tokens_out=usage.completion_tokens if usage else 0,
        )
    score = _coerce_score(parsed)
    score.raw_response = raw
    score.tokens_in = usage.prompt_tokens if usage else 0
    score.tokens_out = usage.completion_tokens if usage else 0
    return score
