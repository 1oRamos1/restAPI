"""Exercise 1.2 - Ticket classification with Structured Outputs.  Task: EXERCISES.md, section 1.2

Run the tests:   pytest 01-llm-basics/tests/test_ex02_classify.py
Try it for real: python 01-llm-basics/run_live.py   (needs ANTHROPIC_API_KEY)
Ask for review:  /review 1.2
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

MODEL = "claude-opus-5-5"

Category = Literal["billing", "technical", "account", "other"]


class TicketClassification(BaseModel):
    # TODO: define the fields:
    #   category        - one of Category
    #   urgency         - int, 1..5 (use Field constraints)
    #   summary         - short Hebrew summary, max 300 chars
    #   suggested_reply - Hebrew draft reply to the customer
    pass


class ClassificationError(Exception):
    """Raised when the model did not produce a usable classification."""


@dataclass(frozen=True)
class ClassificationResult:
    ticket: TicketClassification
    input_tokens: int
    output_tokens: int


# TODO: write a real system prompt. Requirements in EXERCISES.md (role, what each
# category means, the urgency scale with examples, language of the output,
# and how to treat instructions that appear inside the ticket text).
SYSTEM_PROMPT = """
"""


def build_messages(ticket_text: str) -> list[dict]:
    """Return the `messages` list for the API call.

    The ticket text must be stripped and wrapped in <ticket>...</ticket> tags.
    Raise ValueError for empty / whitespace-only input.
    """
    raise NotImplementedError


def classify_ticket(ticket_text: str, client, model: str = MODEL) -> ClassificationResult:
    """Classify one ticket using `client.messages.parse(..., output_format=TicketClassification)`.

    - Handle stop_reason "refusal" and "max_tokens" by raising ClassificationError.
    - Raise ClassificationError if `parsed_output` is missing.
    - Return a ClassificationResult including token usage.
    """
    raise NotImplementedError
