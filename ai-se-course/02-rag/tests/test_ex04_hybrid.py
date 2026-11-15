import os

import pytest

from common.embeddings import HashingEmbedder
from ex01_chunking import chunk_document
from ex03_bm25 import BM25, tokenize
from ex04_hybrid import hybrid_search, rrf

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def test_rrf_scores():
    res = dict(rrf([["a", "b", "c"], ["b", "a"]], k=60))
    assert res["a"] == pytest.approx(1 / 61 + 1 / 62)
    assert res["b"] == pytest.approx(1 / 62 + 1 / 61)
    assert res["c"] == pytest.approx(1 / 63)


def test_rrf_order_and_ties():
    out = rrf([["a", "b", "c"], ["b", "a", "d"]])
    assert [i for i, _ in out][:2] == ["a", "b"]  # tie -> first appearance
    assert [i for i, _ in out][-1] == "d"


def test_rrf_item_in_both_lists_beats_top_of_one():
    out = rrf([["x", "shared"], ["y", "shared"]], k=1)
    # shared: 1/3+1/3=0.667 > x: 1/2
    assert out[0][0] == "shared"


def test_rrf_empty():
    assert rrf([]) == [] and rrf([[], []]) == []


def _index():
    chunks = []
    for name in ["hr-leave", "it-vpn", "finance-expenses", "general-office"]:
        text = open(os.path.join(DATA, f"{name}.md"), encoding="utf-8").read()
        chunks += chunk_document(text, name, max_chars=400, overlap=60)
    emb = HashingEmbedder()
    vecs = emb.embed_many([c.heading + "\n" + c.text for c in chunks])
    bm = BM25([tokenize(c.heading + " " + c.text, strip_hebrew_prefix=True) for c in chunks])
    return chunks, emb, vecs, bm


def test_hybrid_finds_exact_code():
    chunks, emb, vecs, bm = _index()
    tok = lambda q: tokenize(q, strip_hebrew_prefix=True)
    res = hybrid_search("מה הקוד LAP-7731", chunks, emb, bm, tok, chunk_vectors=vecs, top_k=3)
    by_id = {c.id: c for c in chunks}
    assert any("LAP-7731" in by_id[cid].text for cid, _ in res)
    assert len(res) <= 3
    assert all(isinstance(cid, str) for cid, _ in res)


def test_hybrid_returns_sorted_scores():
    chunks, emb, vecs, bm = _index()
    res = hybrid_search("ימי מחלה אישור רפואי", chunks, emb, bm, tokenize, chunk_vectors=vecs, top_k=5)
    scores = [s for _, s in res]
    assert scores == sorted(scores, reverse=True)
