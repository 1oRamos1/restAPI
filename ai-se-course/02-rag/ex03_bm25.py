"""Exercise 2.3 - BM25 keyword search from scratch.  Task: EXERCISES.md, section 2.3

Run the tests:   pytest 02-rag/tests/test_ex03_bm25.py
Ask for review:  /review 2.3
"""
from __future__ import annotations

import math  # noqa: F401  (you will need it)
import re

HEBREW_PREFIXES = "ובהלמשכ"


def tokenize(text: str, *, strip_hebrew_prefix: bool = False) -> list[str]:
    """Lower-case word tokens (unicode \\w+).

    With strip_hebrew_prefix=True, remove ONE leading Hebrew prefix letter
    (one of HEBREW_PREFIXES) from Hebrew words that are longer than 3 letters,
    e.g. "והחזר" -> "החזר", "בחשבון" -> "חשבון". Non-Hebrew tokens are untouched.
    """
    raise NotImplementedError


class BM25:
    """Okapi BM25 over pre-tokenized documents.

    idf(t)      = ln( (N - df(t) + 0.5) / (df(t) + 0.5) + 1 )
    score(d, q) = sum over query terms t of
                  idf(t) * tf(t,d) * (k1 + 1) / ( tf(t,d) + k1 * (1 - b + b * |d| / avgdl) )
    """

    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        # TODO: precompute what you need once (doc lengths, avgdl, term frequencies, df)
        raise NotImplementedError

    def idf(self, term: str) -> float:
        raise NotImplementedError

    def scores(self, query: list[str]) -> list[float]:
        """One score per document, in document order. Repeated query terms count once."""
        raise NotImplementedError

    def top_k(self, query: list[str], k: int) -> list[tuple[int, float]]:
        """(doc_index, score) best first, only documents with score > 0."""
        raise NotImplementedError
