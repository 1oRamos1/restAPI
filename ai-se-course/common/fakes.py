"""Test doubles that mimic the small part of the Anthropic SDK the exercises use.

Tests inject these instead of a real client, so the exercises run offline,
for free, and deterministically. Your code should accept a `client` argument
and only use `client.messages.create(...)` / `client.messages.parse(...)`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any


@dataclass
class FakeUsage:
    input_tokens: int = 100
    output_tokens: int = 50
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class FakeResponse:
    content: list[Any] = field(default_factory=list)
    stop_reason: str = "end_turn"
    usage: FakeUsage = field(default_factory=FakeUsage)
    parsed_output: Any = None


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


class _FakeMessages:
    def __init__(self, responses: list[FakeResponse]):
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def _next(self, kwargs: dict[str, Any]) -> FakeResponse:
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("FakeClient: no more scripted responses (unexpected extra call)")
        r = self._responses.pop(0)
        if isinstance(r, Exception):
            raise r
        return r

    def create(self, **kwargs: Any) -> FakeResponse:
        return self._next(kwargs)

    def parse(self, **kwargs: Any) -> FakeResponse:
        return self._next(kwargs)


class FakeClient:
    """`FakeClient([resp1, resp2])` returns the scripted responses in order.

    After the call, inspect `client.messages.calls` to see exactly what your
    code sent (model, system, messages, ...).
    """

    def __init__(self, responses: list[FakeResponse] | None = None):
        self.messages = _FakeMessages(responses or [])
