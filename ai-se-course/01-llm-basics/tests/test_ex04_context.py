import copy

import pytest

from ex04_context import message_tokens, trim_history


def total(msgs):
    return sum(message_tokens(x) for x in msgs)


def convo(n_pairs, size=300):
    out = []
    for i in range(n_pairs):
        out.append({"role": "user", "content": f"u{i}:" + "א" * size})
        out.append({"role": "assistant", "content": f"a{i}:" + "ב" * size})
    out.append({"role": "user", "content": "השאלה האחרונה"})
    return out


def test_returns_same_when_it_fits():
    msgs = convo(2)
    assert trim_history(msgs, budget=10_000) == msgs


def test_does_not_mutate_input():
    msgs = convo(10)
    snapshot = copy.deepcopy(msgs)
    trim_history(msgs, budget=400)
    assert msgs == snapshot


def test_fits_budget_and_keeps_latest():
    msgs = convo(10)
    out = trim_history(msgs, budget=500)
    assert total(out) <= 500
    assert out[-1] == msgs[-1]


def test_pins_first_message():
    msgs = convo(10)
    out = trim_history(msgs, budget=500, pin_first=True)
    assert out[0] == msgs[0]
    assert total(out) <= 500


def test_without_pin_first_can_drop_it():
    msgs = convo(10)
    out = trim_history(msgs, budget=500, pin_first=False)
    assert msgs[0] not in out


def test_tail_starts_with_user_after_pin():
    msgs = convo(10)
    for budget in range(150, 900, 37):
        out = trim_history(msgs, budget=budget, pin_first=True)
        assert out[0]["role"] == "user"
        if len(out) > 1 and len(out) < len(msgs):
            assert out[1]["role"] == "user", f"orphan assistant turn at budget={budget}"


def test_starts_with_user_without_pin():
    msgs = convo(10)
    for budget in range(60, 900, 41):
        out = trim_history(msgs, budget=budget, pin_first=False)
        assert out[0]["role"] == "user"


def test_kept_messages_are_contiguous_suffix():
    msgs = convo(10)
    out = trim_history(msgs, budget=600, pin_first=False)
    assert out == msgs[len(msgs) - len(out):]


def test_last_message_too_big_raises():
    msgs = [{"role": "user", "content": "א" * 3000}]
    with pytest.raises(ValueError):
        trim_history(msgs, budget=100)


def test_pinned_plus_last_must_fit():
    msgs = [{"role": "user", "content": "א" * 900}, {"role": "assistant", "content": "ok"},
            {"role": "user", "content": "א" * 900}]
    with pytest.raises(ValueError):
        trim_history(msgs, budget=400, pin_first=True)
