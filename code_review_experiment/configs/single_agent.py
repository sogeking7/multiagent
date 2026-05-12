"""Config A — Single Agent.

One LLM call with the entire 600-token output budget. This is the control
condition: it isolates the effect of architectural specialisation by giving
a single model the same total budget that the multi-agent configs split
across roles.
"""

from __future__ import annotations

from ._common import (
    AgentCall,
    ConfigResult,
    call_chat,
    get_sync_client,
)


CONFIG_NAME = "A_single_agent"

# Budget allocated per the experiment design.
TOTAL_BUDGET = 600

SYSTEM_PROMPT = (
    "You are an expert code reviewer. Review the provided code thoroughly. "
    "Identify all issues including logic bugs, security vulnerabilities, and "
    "style problems. For each issue: state the issue type, the line or area "
    "affected, and a brief explanation. Be concise. Format: numbered list."
)


def run(code: str) -> ConfigResult:
    client = get_sync_client()
    call: AgentCall = call_chat(
        client,
        system=SYSTEM_PROMPT,
        user=code,
        max_tokens=TOTAL_BUDGET,
        agent_role="single_reviewer",
    )
    return ConfigResult(
        config_name=CONFIG_NAME,
        final_output=call.output,
        agent_calls=[call],
        error=call.error,
    )
