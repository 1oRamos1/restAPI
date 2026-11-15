"""Exercise 2.2 - Cosine similarity and top-k search with numpy.  Task: EXERCISES.md, section 2.2

Run the tests:   pytest 02-rag/tests/test_ex02_vector_search.py
Ask for review:  /review 2.2
"""
from __future__ import annotations

import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine of the angle between two 1-D vectors. Return 0.0 if either is all zeros."""
    raise NotImplementedError


def top_k(query: np.ndarray, matrix: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Return the k rows of `matrix` most similar to `query`, as (row_index, score),
    best first. Must be vectorised (no Python loop over rows).

    - Rows that are all zeros get score 0.0 (no division-by-zero warnings).
    - If k > number of rows, return all rows. k <= 0 -> ValueError.
    - Ties are broken by the lower row index.
    """
    raise NotImplementedError
