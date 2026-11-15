import pytest

from ex03_retry import backoff_delay, call_with_retry, is_retryable


class APIError(Exception):
    def __init__(self, status_code, retry_after=None):
        super().__init__(f"status {status_code}")
        self.status_code = status_code
        if retry_after is not None:
            self.retry_after = retry_after


def flaky(errors, result="ok"):
    """Return a fn that raises the given errors in order, then returns result."""
    errors = list(errors)
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if errors:
            raise errors.pop(0)
        return result
    fn.calls = calls
    return fn


@pytest.mark.parametrize("exc,expected", [
    (APIError(429), True), (APIError(500), True), (APIError(503), True), (APIError(529), True),
    (APIError(408), True), (APIError(409), True),
    (APIError(400), False), (APIError(401), False), (APIError(404), False), (APIError(422), False),
    (ConnectionError(), True), (TimeoutError(), True), (ConnectionResetError(), True),
    (ValueError(), False), (KeyError(), False),
])
def test_is_retryable(exc, expected):
    assert is_retryable(exc) is expected


def test_backoff_grows_and_is_capped():
    top = lambda: 0.999999
    assert backoff_delay(0, base=1, cap=30, rng=top) == pytest.approx(1, rel=1e-3)
    assert backoff_delay(3, base=1, cap=30, rng=top) == pytest.approx(8, rel=1e-3)
    assert backoff_delay(10, base=1, cap=30, rng=top) == pytest.approx(30, rel=1e-3)


def test_backoff_has_jitter():
    assert backoff_delay(3, rng=lambda: 0.0) == 0
    assert backoff_delay(3, rng=lambda: 0.5) == pytest.approx(4)


def test_succeeds_after_transient_errors():
    sleeps = []
    fn = flaky([APIError(529), ConnectionError()])
    assert call_with_retry(fn, sleep=sleeps.append, rng=lambda: 0.5) == "ok"
    assert fn.calls["n"] == 3
    assert sleeps == [pytest.approx(0.5), pytest.approx(1.0)]


def test_non_retryable_raises_immediately():
    sleeps = []
    fn = flaky([APIError(400)])
    with pytest.raises(APIError):
        call_with_retry(fn, sleep=sleeps.append)
    assert fn.calls["n"] == 1 and sleeps == []


def test_gives_up_after_max_attempts():
    sleeps = []
    fn = flaky([APIError(500)] * 10)
    with pytest.raises(APIError):
        call_with_retry(fn, max_attempts=3, sleep=sleeps.append, rng=lambda: 0.1)
    assert fn.calls["n"] == 3
    assert len(sleeps) == 2, "no sleep after the final failed attempt"


def test_respects_retry_after():
    sleeps = []
    fn = flaky([APIError(429, retry_after=7)])
    call_with_retry(fn, sleep=sleeps.append, rng=lambda: 0.1)
    assert sleeps[0] >= 7


def test_on_retry_hook_called():
    seen = []
    fn = flaky([APIError(503)])
    call_with_retry(fn, sleep=lambda s: None, rng=lambda: 0.5,
                    on_retry=lambda attempt, exc, delay: seen.append((attempt, type(exc), delay)))
    assert seen == [(0, APIError, pytest.approx(0.5))]


def test_max_attempts_must_be_positive():
    with pytest.raises(ValueError):
        call_with_retry(lambda: 1, max_attempts=0)
