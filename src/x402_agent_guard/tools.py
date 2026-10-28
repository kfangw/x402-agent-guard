"""Payment tools offered to a model: `check_payment` and `pay`.

One implementation serves every front end (MCP server, plain agent loop, frameworks),
so argument checks and the route through the guard are the same everywhere.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from x402_agent_guard.guard import Guard
from x402_agent_guard.policy import PaymentRequest


class ToolError(ValueError):
    """Bad tool name or arguments. Reported back to the model, never raised past the loop."""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema for the arguments object


_PAYMENT_PARAMS = {
    "type": "object",
    "properties": {
        "payee": {"type": "string", "description": "Address or id of the party to pay."},
        "amount": {
            "type": "integer",
            "description": "Amount in the asset's smallest unit (USDC: 6 decimals).",
        },
        "resource": {"type": "string", "description": "What the payment is for, e.g. a URL."},
    },
    "required": ["payee", "amount"],
    "additionalProperties": False,
}


@dataclass
class PaymentTools:
    guard: Guard
    agent_id: str
    asset: str
    clock: Callable[[], float] = field(default=time.time)

    def specs(self) -> list[ToolSpec]:
        unit = f"Amount is an integer in {self.asset} base units."
        return [
            ToolSpec(
                "check_payment",
                f"Check whether a payment would be allowed. {unit}",
                _PAYMENT_PARAMS,
            ),
            ToolSpec(
                "pay",
                f"Pay if policy allows. Payments that need approval are refused. {unit}",
                _PAYMENT_PARAMS,
            ),
        ]

    def check_payment(self, payee: str, amount: int, resource: str = "") -> dict:
        d = self.guard.engine.evaluate(self._request(payee, amount, resource))
        return {"outcome": d.outcome.value, "reason": d.reason}

    def pay(self, payee: str, amount: int, resource: str = "") -> dict:
        result = self.guard.request_payment(self._request(payee, amount, resource))
        out = {"outcome": result.decision.outcome.value, "reason": result.decision.reason}
        if result.receipt:
            out["tx_ref"] = result.receipt.tx_ref
        return out

    def call(self, name: str, arguments: dict[str, Any]) -> dict:
        """Dispatch a tool call by name with JSON arguments from a model."""
        if name not in ("check_payment", "pay"):
            raise ToolError(f"unknown tool: {name}")
        if not isinstance(arguments, dict):
            raise ToolError("arguments must be an object")
        extra = set(arguments) - {"payee", "amount", "resource"}
        if extra:
            raise ToolError(f"unexpected arguments: {sorted(extra)}")
        try:
            payee, amount = arguments["payee"], arguments["amount"]
        except KeyError as e:
            raise ToolError(f"missing argument: {e.args[0]}") from None
        resource = arguments.get("resource", "")
        return getattr(self, name)(payee, amount, resource)

    def _request(self, payee: object, amount: object, resource: object) -> PaymentRequest:
        # Models emit JSON; reject anything that is not exactly an int amount rather than
        # coercing "250000" or 0.25 into a payment.
        if not isinstance(payee, str) or not payee:
            raise ToolError("payee must be a non-empty string")
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise ToolError("amount must be an integer in base units")
        if not isinstance(resource, str):
            raise ToolError("resource must be a string")
        return PaymentRequest(self.agent_id, payee, amount, self.asset, resource, self.clock())
