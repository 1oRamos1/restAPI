"""Exercise 1.1 - Token cost calculator.  Task description: EXERCISES.md, section 1.1

Run the tests:   pytest 01-llm-basics/tests/test_ex01_cost.py
Ask for review:  /review 1.1
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    """Prices in USD per 1M tokens."""

    input_per_mtok: float
    output_per_mtok: float
    cache_read_multiplier: float = 0.1    # cache reads cost ~10% of base input
    cache_write_multiplier: float = 1.25  # writing to cache costs ~125% of base input


@dataclass(frozen=True)
class Usage:
    """Mirrors `response.usage` from the API.

    NOTE: `input_tokens` counts only the *uncached* input tokens.
    Cached tokens are reported separately.
    """

    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


def request_cost(usage: Usage, price: Price) -> float:
    """Return the USD cost of a single request."""
    # TODO 1: raise ValueError if any token count is negative
    # TODO 2: sum the four token types, each at its own rate
    raise NotImplementedError


def monthly_estimate(
    requests_per_month: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    price: Price,
    *,
    cache_hit_ratio: float = 0.0,
    batch_share: float = 0.0,
    batch_discount: float = 0.5,
    calls_per_request: int = 1,
) -> float:
    """Estimate the monthly USD cost of a workload.

    - avg_input_tokens: ALL input tokens of one model call (cached + uncached)
    - cache_hit_ratio: fraction of input tokens served from cache (0..1)
    - batch_share: fraction of requests sent through the Batch API (0..1)
    - batch_discount: discount for batched requests (0.5 = 50% off)
    - calls_per_request: an agent may call the model several times per user request
    """
    # TODO: validate inputs (ratios in [0, 1], non-negative numbers, calls_per_request >= 1)
    # TODO: compute the cost. Ignore cache-write costs for the monthly estimate.
    raise NotImplementedError
