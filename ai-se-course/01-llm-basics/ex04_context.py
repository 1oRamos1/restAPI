"""Exercise 1.4 - Keep a conversation inside a token budget.  Task: EXERCISES.md, section 1.4

Run the tests:   pytest 01-llm-basics/tests/test_ex04_context.py
Ask for review:  /review 1.4
"""
from __future__ import annotations

Message = dict  # {"role": "user" | "assistant", "content": str}


def approx_tokens(text: str) -> int:
    """Rough token estimate (given - do not change).

    Real code should use the provider's token-counting endpoint. Hebrew usually
    needs more tokens per character than English, so this errs on the high side.
    """
    return len(text) // 3 + 1


def message_tokens(msg: Message) -> int:
    """Tokens of one message: its content plus 4 tokens of per-message overhead."""
    return approx_tokens(msg["content"]) + 4


def trim_history(messages: list[Message], budget: int, *, pin_first: bool = True) -> list[Message]:
    """Return a new list that fits in `budget` tokens. Rules (see EXERCISES.md):

    1. Never modify the input list.
    2. Keep the most recent messages; drop the oldest first.
    3. If `pin_first`, the first message (the original task) is always kept,
       and it counts toward the budget.
    4. If anything was dropped, the kept tail (after the pinned message) must
       start with a "user" message - an assistant reply whose question was
       dropped is an orphan. Without pin_first, the result starts with "user".
    5. The last message must always be kept. If it can't fit, raise ValueError.
    """
    raise NotImplementedError
