"""Exercise 2.5 - Measuring retrieval quality.  Task: EXERCISES.md, section 2.5

Run the tests:   pytest 02-rag/tests/test_ex05_retrieval_eval.py
Ask for review:  /review 2.5
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Fraction of the relevant ids found in the first k retrieved. relevant empty -> ValueError."""
    raise NotImplementedError


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    """1 / (position of the first relevant id, starting at 1), or 0.0 if none."""
    raise NotImplementedError


@dataclass
class EvalReport:
    recall: float                 # mean recall@k over the golden set
    mrr: float                    # mean reciprocal rank
    failures: list[str] = field(default_factory=list)  # questions with recall@k == 0


def evaluate(retrieve: Callable[[str], list[str]], golden: list[dict], k: int = 5) -> EvalReport:
    """golden: [{"question": str, "relevant": [chunk_id, ...]}, ...]  (non-empty)

    Call `retrieve(question)` once per question; it returns ranked chunk ids.
    """
    raise NotImplementedError
