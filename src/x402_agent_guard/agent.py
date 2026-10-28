"""A plain agent loop over any LLM API with tool calling. No framework.

    messages -> model (with tool specs) -> tool calls -> PaymentTools -> Guard -> results -> model

The loop stops when the model answers without a tool call, or at `max_steps` model turns.
`Model` is the only provider-specific piece; `ScriptedModel` replays fixed turns for tests.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from x402_agent_guard.tools import PaymentTools, ToolError, ToolSpec


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Message:
    role: Literal["user", "assistant", "tool"]
    content: str
    tool_calls: tuple[ToolCall, ...] = ()  # assistant messages only
    tool_call_id: str | None = None  # tool messages only


@dataclass(frozen=True)
class ModelTurn:
    text: str = ""
    tool_calls: tuple[ToolCall, ...] = ()


class Model(Protocol):
    """Adapter to one LLM provider. Translate messages and specs to its API and back."""

    def complete(self, messages: Sequence[Message], tools: Sequence[ToolSpec]) -> ModelTurn: ...


@dataclass(frozen=True)
class AgentRun:
    messages: tuple[Message, ...]
    answer: str
    stopped: Literal["answered", "step_limit"]


def run_agent(model: Model, tools: PaymentTools, prompt: str, max_steps: int = 8) -> AgentRun:
    messages = [Message("user", prompt)]
    specs = tools.specs()
    for _ in range(max_steps):
        turn = model.complete(tuple(messages), specs)
        messages.append(Message("assistant", turn.text, turn.tool_calls))
        if not turn.tool_calls:
            return AgentRun(tuple(messages), turn.text, "answered")
        for call in turn.tool_calls:
            try:
                result = tools.call(call.name, call.arguments)
            except ToolError as e:
                result = {"error": str(e)}
            messages.append(Message("tool", json.dumps(result), tool_call_id=call.id))
    return AgentRun(tuple(messages), "", "step_limit")


@dataclass
class ScriptedModel:
    """Returns `turns` in order and records what it was shown. For tests and demos."""

    turns: list[ModelTurn]
    seen: list[tuple[Message, ...]] = field(default_factory=list)

    def complete(self, messages: Sequence[Message], tools: Sequence[ToolSpec]) -> ModelTurn:
        self.seen.append(tuple(messages))
        if not self.turns:
            raise RuntimeError("scripted model ran out of turns")
        return self.turns.pop(0)
