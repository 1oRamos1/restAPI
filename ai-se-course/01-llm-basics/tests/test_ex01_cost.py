import pytest

from ex01_cost import Price, Usage, monthly_estimate, request_cost

P = Price(input_per_mtok=2.0, output_per_mtok=10.0)


def test_simple_request():
    # 1M input at $2 + 100k output at $10/M = 2 + 1 = 3
    assert request_cost(Usage(1_000_000, 100_000), P) == pytest.approx(3.0)


def test_cache_read_and_write_priced_differently():
    u = Usage(input_tokens=0, output_tokens=0,
              cache_read_input_tokens=1_000_000, cache_creation_input_tokens=1_000_000)
    # read: 2 * 0.1 = 0.2 ; write: 2 * 1.25 = 2.5
    assert request_cost(u, P) == pytest.approx(2.7)


def test_negative_tokens_rejected():
    with pytest.raises(ValueError):
        request_cost(Usage(-1, 10), P)


def test_monthly_basic():
    # 10k req * (4000 in, 500 out) = 40M in, 5M out => 80 + 50 = 130
    assert monthly_estimate(10_000, 4000, 500, P) == pytest.approx(130.0)


def test_monthly_with_cache():
    # half of 40M input read from cache: 20M*2 + 20M*0.2 = 40 + 4 = 44 ; output 50
    assert monthly_estimate(10_000, 4000, 500, P, cache_hit_ratio=0.5) == pytest.approx(94.0)


def test_monthly_with_batch():
    # 40% of requests batched at 50% off: 130 * (0.6 + 0.4*0.5) = 104
    assert monthly_estimate(10_000, 4000, 500, P, batch_share=0.4) == pytest.approx(104.0)


def test_agent_calls_multiply_cost():
    assert monthly_estimate(10_000, 4000, 500, P, calls_per_request=3) == pytest.approx(390.0)


def test_zero_requests_is_free():
    assert monthly_estimate(0, 4000, 500, P) == 0


@pytest.mark.parametrize("kwargs", [
    {"cache_hit_ratio": 1.5}, {"cache_hit_ratio": -0.1},
    {"batch_share": 2}, {"calls_per_request": 0},
])
def test_monthly_validation(kwargs):
    with pytest.raises(ValueError):
        monthly_estimate(10, 10, 10, P, **kwargs)


def test_monthly_negative_volume_rejected():
    with pytest.raises(ValueError):
        monthly_estimate(-5, 10, 10, P)
