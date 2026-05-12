"""Config B — Sequential Multi-Agent.

Three specialist agents run in order. Each agent's prompt contains the
original code plus all earlier reviews, with an explicit role restriction
and an instruction to avoid duplicating prior findings. Each agent is
limited to 200 output tokens, keeping the total at 600 to match Config A.
"""

from __future__ import annotations

from ._common import (
    AgentCall,
    ConfigResult,
    call_chat,
    get_sync_client,
)


CONFIG_NAME = "B_sequential_multi"

PER_AGENT_BUDGET = 200

LOGIC_SYSTEM = (
    "You are a senior software engineer reviewing code SPECIFICALLY for LOGIC "
    "and CORRECTNESS issues only. Examples: off-by-one errors, wrong "
    "conditionals, missing edge cases, incorrect return values, mutable "
    "default arguments, closure-capture bugs. Do NOT comment on security or "
    "style. For each issue: state the type, the line/area, and a brief "
    "explanation. Be concise. Format: numbered list."
)

SECURITY_SYSTEM = (
    "You are a senior application security engineer reviewing code "
    "SPECIFICALLY for SECURITY vulnerabilities only. Examples: injection, "
    "insecure deserialization, weak crypto, hardcoded secrets, SSRF, path "
    "traversal, XSS. Do NOT comment on general logic bugs or style. You may "
    "reference Agent 1's logic findings to avoid duplication, but only "
    "report security issues. For each issue: state the type, the line/area, "
    "and a brief explanation. Be concise. Format: numbered list."
)

STYLE_SYSTEM = (
    "You are a senior software engineer reviewing code SPECIFICALLY for "
    "STYLE, READABILITY, and MAINTAINABILITY issues only. Examples: poor "
    "naming, magic numbers, deep nesting, missing error handling, DRY "
    "violations, inconsistent return types, single-responsibility "
    "violations. Do NOT re-report logic or security issues already raised "
    "by previous agents. For each issue: state the type, the line/area, "
    "and a brief explanation. Be concise. Format: numbered list."
)


def _build_user_prompt(code: str, prior_reviews: list[tuple[str, str]]) -> str:
    """Assemble code + any prior reviews for downstream agents."""
    sections = ["CODE UNDER REVIEW:", "```python", code, "```"]
    for role, text in prior_reviews:
        sections.append(f"\nPREVIOUS REVIEW — {role}:\n{text}")
    return "\n".join(sections)


def run(code: str) -> ConfigResult:
    client = get_sync_client()
    calls: list[AgentCall] = []
    prior: list[tuple[str, str]] = []

    for role, system_prompt in (
        ("logic_reviewer", LOGIC_SYSTEM),
        ("security_reviewer", SECURITY_SYSTEM),
        ("style_reviewer", STYLE_SYSTEM),
    ):
        call = call_chat(
            client,
            system=system_prompt,
            user=_build_user_prompt(code, prior),
            max_tokens=PER_AGENT_BUDGET,
            agent_role=role,
        )
        calls.append(call)
        # Even if a call errored, downstream agents still see whatever text
        # came back (empty string on error) — they will simply have no prior
        # context to deduplicate against.
        prior.append((role, call.output))

    final_output = _stitch_reviews(calls)
    errors = [c.error for c in calls if c.error]
    return ConfigResult(
        config_name=CONFIG_NAME,
        final_output=final_output,
        agent_calls=calls,
        error="; ".join(errors) if errors else None,
    )


def _stitch_reviews(calls: list[AgentCall]) -> str:
    """The judge sees the concatenated output of all three agents.

    We label each section so the judge knows the structure, but we do not
    add an aggregator (that is Config C's role). The final_output here is
    raw concatenation of specialist reviews — that is the artifact the
    sequential architecture produces in this design.
    """
    parts: list[str] = []
    for call in calls:
        parts.append(f"### {call.agent_role}\n{call.output.strip()}")
    return "\n\n".join(parts)
