"""Config C — Parallel Multi-Agent.

Three specialist agents run concurrently (asyncio.gather) on the same code.
None of the specialists sees the others' output. A fourth aggregator agent
then merges their findings into a single deduplicated review.

Budget: 150 tokens per specialist (3 x 150 = 450) + 150 for the aggregator
= 600 total, matching Config A and Config B.
"""

from __future__ import annotations

import asyncio

from ._common import (
    AgentCall,
    ConfigResult,
    call_chat_async,
    get_async_client,
)


CONFIG_NAME = "C_parallel_multi"

SPECIALIST_BUDGET = 150
AGGREGATOR_BUDGET = 150

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
    "traversal, XSS. Do NOT comment on general logic bugs or style. For "
    "each issue: state the type, the line/area, and a brief explanation. "
    "Be concise. Format: numbered list."
)

STYLE_SYSTEM = (
    "You are a senior software engineer reviewing code SPECIFICALLY for "
    "STYLE, READABILITY, and MAINTAINABILITY issues only. Examples: poor "
    "naming, magic numbers, deep nesting, missing error handling, DRY "
    "violations, inconsistent return types, single-responsibility "
    "violations. Do NOT comment on logic or security issues. For each "
    "issue: state the type, the line/area, and a brief explanation. Be "
    "concise. Format: numbered list."
)

AGGREGATOR_SYSTEM = (
    "You are a senior code review coordinator. You have received three "
    "independent reviews of the same code from specialist agents. Your "
    "job is to:\n"
    "1. Merge their findings, removing exact duplicates\n"
    "2. Resolve any contradictions\n"
    "3. Output a clean, unified numbered list of all unique issues found\n"
    "Be concise. Do not add new issues not mentioned by the specialists."
)


def _user_for_specialist(code: str) -> str:
    return f"CODE UNDER REVIEW:\n```python\n{code}\n```"


def _user_for_aggregator(code: str, reviews: list[tuple[str, str]]) -> str:
    parts = ["CODE UNDER REVIEW:", "```python", code, "```", ""]
    for role, text in reviews:
        parts.append(f"REVIEW — {role}:\n{text}\n")
    return "\n".join(parts)


async def _run_async(code: str) -> ConfigResult:
    client = get_async_client()
    user_msg = _user_for_specialist(code)

    specialist_coros = [
        call_chat_async(
            client,
            system=LOGIC_SYSTEM,
            user=user_msg,
            max_tokens=SPECIALIST_BUDGET,
            agent_role="logic_reviewer",
        ),
        call_chat_async(
            client,
            system=SECURITY_SYSTEM,
            user=user_msg,
            max_tokens=SPECIALIST_BUDGET,
            agent_role="security_reviewer",
        ),
        call_chat_async(
            client,
            system=STYLE_SYSTEM,
            user=user_msg,
            max_tokens=SPECIALIST_BUDGET,
            agent_role="style_reviewer",
        ),
    ]
    specialist_calls: list[AgentCall] = await asyncio.gather(*specialist_coros)

    aggregator_call = await call_chat_async(
        client,
        system=AGGREGATOR_SYSTEM,
        user=_user_for_aggregator(
            code, [(c.agent_role, c.output) for c in specialist_calls]
        ),
        max_tokens=AGGREGATOR_BUDGET,
        agent_role="aggregator",
    )

    all_calls = specialist_calls + [aggregator_call]
    errors = [c.error for c in all_calls if c.error]
    return ConfigResult(
        config_name=CONFIG_NAME,
        final_output=aggregator_call.output,
        agent_calls=all_calls,
        error="; ".join(errors) if errors else None,
    )


def run(code: str) -> ConfigResult:
    """Synchronous wrapper around the async pipeline so callers do not need
    to know which configs are async."""
    return asyncio.run(_run_async(code))
