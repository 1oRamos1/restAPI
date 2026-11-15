"""Exercise 1.3 - Retries with exponential backoff and jitter.  Task: EXERCISES.md, section 1.3

Run the tests:   pytest 01-llm-basics/tests/test_ex03_retry.py
Ask for review:  /review 1.3
"""
from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")

RETRYABLE_STATUS = {408, 409, 429}


def is_retryable(exc: BaseException) -> bool:
    """True for transient failures that are worth retrying.

    - exceptions with a `status_code` attribute: 408, 409, 429 and any 5xx
    - ConnectionError and TimeoutError (and subclasses)
    - everything else: False
    """
    raise NotImplementedError


def backoff_delay(attempt: int, base: float = 1.0, cap: float = 30.0,
                  rng: Callable[[], float] = random.random) -> float:
    """'Full jitter' backoff: a random value in [0, min(cap, base * 2**attempt)).

    `attempt` starts at 0 for the first retry.
    """
    raise NotImplementedError


def call_with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 4,
    base: float = 1.0,
    cap: float = 30.0,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> T:
    """Call `fn()` and retry transient failures.

    - Total calls never exceed `max_attempts`.
    - Non-retryable errors are re-raised immediately (no sleep).
    - If the exception has a numeric `retry_after` attribute (seconds, from the
      server's Retry-After header), wait at least that long.
    - Call `on_retry(attempt, exc, delay)` before each sleep (useful for logging).
    - When attempts run out, re-raise the last exception.
    """
    raise NotImplementedError
