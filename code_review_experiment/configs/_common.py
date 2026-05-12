"""Shared helpers for the three review configurations.

Centralises three things:
  1. Client construction (sync + async) reading OPENAI_API_KEY from env.
  2. A typed result container (`ConfigResult`) every config returns.
  3. The exact AGENT_MODEL identifier so all configs stay in lockstep.

Each config is otherwise free to define its own prompts and call orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI, OpenAI


# Model identifiers are pinned here so the experiment is reproducible. The
# README documents why these specific models were chosen.
AGENT_MODEL = "gpt-4o-mini"
JUDGE_MODEL = "gpt-4o"

# Sampling temperature for agents. Kept low but non-zero so multi-agent
# specialists do not produce literally identical text, which would inflate
# the redundancy metric for Config C.
AGENT_TEMPERATURE = 0.2

# OpenAI price points (USD per 1M tokens) for gpt-4o-mini, per the prompt.
PRICE_IN_PER_M = 0.15
PRICE_OUT_PER_M = 0.60


@dataclass
class AgentCall:
    """One round-trip to the LLM, captured for downstream analysis."""

    agent_role: str
    max_tokens: int
    tokens_in: int
    tokens_out: int
    output: str
    error: str | None = None


@dataclass
class ConfigResult:
    """What every config's run() function returns."""

    config_name: str
    final_output: str
    agent_calls: list[AgentCall] = field(default_factory=list)
    error: str | None = None

    @property
    def total_tokens_in(self) -> int:
        return sum(c.tokens_in for c in self.agent_calls)

    @property
    def total_tokens_out(self) -> int:
        return sum(c.tokens_out for c in self.agent_calls)

    @property
    def total_tokens(self) -> int:
        return self.total_tokens_in + self.total_tokens_out

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_name": self.config_name,
            "final_output": self.final_output,
            "error": self.error,
            "total_tokens_in": self.total_tokens_in,
            "total_tokens_out": self.total_tokens_out,
            "total_tokens": self.total_tokens,
            "agent_calls": [
                {
                    "agent_role": c.agent_role,
                    "max_tokens": c.max_tokens,
                    "tokens_in": c.tokens_in,
                    "tokens_out": c.tokens_out,
                    "output": c.output,
                    "error": c.error,
                }
                for c in self.agent_calls
            ],
        }


def get_sync_client() -> OpenAI:
    return OpenAI()


def get_async_client() -> AsyncOpenAI:
    return AsyncOpenAI()


def call_chat(
    client: OpenAI,
    *,
    system: str,
    user: str,
    max_tokens: int,
    agent_role: str,
    model: str = AGENT_MODEL,
    temperature: float = AGENT_TEMPERATURE,
) -> AgentCall:
    """Synchronous chat completion that always returns an AgentCall.

    Errors are captured into AgentCall.error rather than raised, so the
    experiment runner can continue on partial failures (per the prompt:
    'catch and log any API errors without crashing').
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except Exception as exc:  # noqa: BLE001  (boundary: log-and-continue)
        return AgentCall(
            agent_role=agent_role,
            max_tokens=max_tokens,
            tokens_in=0,
            tokens_out=0,
            output="",
            error=f"{type(exc).__name__}: {exc}",
        )

    content = response.choices[0].message.content or ""
    usage = response.usage
    return AgentCall(
        agent_role=agent_role,
        max_tokens=max_tokens,
        tokens_in=usage.prompt_tokens if usage else 0,
        tokens_out=usage.completion_tokens if usage else 0,
        output=content,
    )


async def call_chat_async(
    client: AsyncOpenAI,
    *,
    system: str,
    user: str,
    max_tokens: int,
    agent_role: str,
    model: str = AGENT_MODEL,
    temperature: float = AGENT_TEMPERATURE,
) -> AgentCall:
    """Async sibling of call_chat for parallel configurations."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    except Exception as exc:  # noqa: BLE001
        return AgentCall(
            agent_role=agent_role,
            max_tokens=max_tokens,
            tokens_in=0,
            tokens_out=0,
            output="",
            error=f"{type(exc).__name__}: {exc}",
        )

    content = response.choices[0].message.content or ""
    usage = response.usage
    return AgentCall(
        agent_role=agent_role,
        max_tokens=max_tokens,
        tokens_in=usage.prompt_tokens if usage else 0,
        tokens_out=usage.completion_tokens if usage else 0,
        output=content,
    )
