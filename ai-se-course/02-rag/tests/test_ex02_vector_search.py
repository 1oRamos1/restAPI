import warnings

import numpy as np
import pytest

from ex02_vector_search import cosine_similarity, top_k


def test_cosine_basics():
    assert cosine_similarity(np.array([1.0, 0]), np.array([1.0, 0])) == pytest.approx(1)
    assert cosine_similarity(np.array([1.0, 0]), np.array([0, 2.0])) == pytest.approx(0)
    assert cosine_similarity(np.array([1.0, 1]), np.array([-1.0, -1])) == pytest.approx(-1)
    # scale does not matter
    assert cosine_similarity(np.array([3.0, 4]), np.array([6.0, 8])) == pytest.approx(1)


def test_cosine_zero_vector():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert cosine_similarity(np.zeros(3), np.array([1.0, 2, 3])) == 0.0


def test_top_k_order_and_scores():
    m = np.array([[1, 0], [0, 1], [1, 1], [-1, 0]], dtype=float)
    res = top_k(np.array([1.0, 0.1]), m, k=2)
    assert [i for i, _ in res] == [0, 2]
    assert res[0][1] == pytest.approx(cosine_similarity(np.array([1.0, 0.1]), m[0]))


def test_top_k_more_than_rows():
    m = np.eye(3)
    assert len(top_k(np.array([1.0, 0, 0]), m, k=10)) == 3


def test_top_k_zero_rows_and_ties():
    m = np.array([[0, 0], [2, 0], [5, 0]], dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        res = top_k(np.array([1.0, 0]), m, k=3)
    assert [i for i, _ in res] == [1, 2, 0]   # tie 1 vs 2 -> lower index first
    assert res[-1][1] == 0.0


def test_top_k_invalid_k():
    with pytest.raises(ValueError):
        top_k(np.array([1.0]), np.array([[1.0]]), k=0)


def test_top_k_returns_python_types():
    res = top_k(np.array([1.0, 0]), np.eye(2), k=1)
    assert type(res[0][0]) is int and type(res[0][1]) is float
