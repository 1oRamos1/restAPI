"""Exercise 2.4 - Hybrid search with Reciprocal Rank Fusion.  Task: EXERCISES.md, section 2.4

Run the tests:   pytest 02-rag/tests/test_ex04_hybrid.py
Ask for review:  /review 2.4
"""
from __future__ import annotations

from typing import Hashable, Sequence


def rrf(rankings: Sequence[Sequence[Hashable]], k: int = 60) -> list[tuple[Hashable, float]]:
    """Fuse ranked lists of ids.

    score(id) = sum over lists containing id of 1 / (k + rank), rank starting at 1.
    Return (id, score) sorted by score desc; ties broken by first appearance
    (earliest list, then earliest position).
    """
    raise NotImplementedError


def hybrid_search(query: str, chunks: list, embedder, bm25, tokenize, *,
                  chunk_vectors, top_k: int = 5, candidates: int = 20) -> list[tuple[str, float]]:
    """Return [(chunk.id, rrf_score)] for the best `top_k` chunks.

    - Vector side: embed the query, take the `candidates` best chunks by cosine
      (reuse ex02_vector_search.top_k with `chunk_vectors`).
    - Keyword side: `bm25.top_k(tokenize(query), candidates)`.
    - Fuse the two rankings of chunk ids with rrf().
    """
    raise NotImplementedError
