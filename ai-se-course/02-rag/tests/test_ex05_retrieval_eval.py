import pytest

from ex05_retrieval_eval import EvalReport, evaluate, recall_at_k, reciprocal_rank


def test_recall_at_k():
    assert recall_at_k(["a", "b", "c"], {"b"}, 2) == 1.0
    assert recall_at_k(["a", "b", "c"], {"c"}, 2) == 0.0
    assert recall_at_k(["a", "b", "c"], {"a", "c", "z"}, 3) == pytest.approx(2 / 3)


def test_recall_empty_relevant():
    with pytest.raises(ValueError):
        recall_at_k(["a"], set(), 1)


def test_reciprocal_rank():
    assert reciprocal_rank(["a", "b", "c"], {"c"}) == pytest.approx(1 / 3)
    assert reciprocal_rank(["a", "b"], {"b", "a"}) == 1.0
    assert reciprocal_rank(["a"], {"z"}) == 0.0


def test_evaluate():
    golden = [
        {"question": "q1", "relevant": ["a"]},
        {"question": "q2", "relevant": ["x"]},
        {"question": "q3", "relevant": ["c", "d"]},
    ]
    answers = {"q1": ["a", "b"], "q2": ["b", "c"], "q3": ["b", "c"]}
    calls = []

    def retrieve(q):
        calls.append(q)
        return answers[q]

    rep = evaluate(retrieve, golden, k=2)
    assert isinstance(rep, EvalReport)
    assert calls == ["q1", "q2", "q3"]
    assert rep.recall == pytest.approx((1 + 0 + 0.5) / 3)
    assert rep.mrr == pytest.approx((1 + 0 + 0.5) / 3)
    assert rep.failures == ["q2"]


def test_evaluate_empty_golden():
    with pytest.raises(ValueError):
        evaluate(lambda q: [], [], k=3)
