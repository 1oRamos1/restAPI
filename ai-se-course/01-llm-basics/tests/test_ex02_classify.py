import pytest
from pydantic import ValidationError

from common.fakes import FakeClient, FakeResponse, FakeUsage
from ex02_classify import (
    SYSTEM_PROMPT, ClassificationError, ClassificationResult,
    TicketClassification, build_messages, classify_ticket,
)


def _ticket(**kw):
    data = dict(category="billing", urgency=4, summary="חיוב כפול", suggested_reply="שלום, נבדוק")
    data.update(kw)
    return TicketClassification(**data)


# --- schema -------------------------------------------------------------

def test_schema_accepts_valid():
    t = _ticket()
    assert t.category == "billing" and t.urgency == 4


@pytest.mark.parametrize("bad", [{"category": "refund"}, {"urgency": 0}, {"urgency": 6},
                                 {"summary": "x" * 301}])
def test_schema_rejects_invalid(bad):
    with pytest.raises(ValidationError):
        _ticket(**bad)


def test_schema_requires_all_fields():
    with pytest.raises(ValidationError):
        TicketClassification(category="other", urgency=1)


# --- prompt ---------------------------------------------------------------

def test_system_prompt_is_substantial():
    assert len(SYSTEM_PROMPT.strip()) > 300, "the system prompt is too thin - see EXERCISES.md"


@pytest.mark.parametrize("word", ["billing", "technical", "account", "other"])
def test_system_prompt_explains_every_category(word):
    assert word in SYSTEM_PROMPT


def test_system_prompt_mentions_ticket_tags():
    assert "<ticket>" in SYSTEM_PROMPT or "ticket" in SYSTEM_PROMPT.lower()


def test_build_messages_wraps_and_strips():
    msgs = build_messages("   הכסף ירד פעמיים  \n")
    assert msgs == [{"role": "user", "content": "<ticket>\nהכסף ירד פעמיים\n</ticket>"}]


@pytest.mark.parametrize("empty", ["", "   ", "\n\t"])
def test_build_messages_rejects_empty(empty):
    with pytest.raises(ValueError):
        build_messages(empty)


# --- API call -------------------------------------------------------------

def test_classify_sends_correct_request():
    client = FakeClient([FakeResponse(parsed_output=_ticket(), usage=FakeUsage(120, 60))])
    result = classify_ticket("חויבתי פעמיים", client)

    call = client.messages.calls[0]
    assert call["output_format"] is TicketClassification
    assert call["system"] == SYSTEM_PROMPT
    assert call["messages"] == build_messages("חויבתי פעמיים")
    assert call["model"]
    assert 0 < call["max_tokens"] <= 4000, "a classification needs a small, explicit max_tokens"

    assert isinstance(result, ClassificationResult)
    assert result.ticket.category == "billing"
    assert (result.input_tokens, result.output_tokens) == (120, 60)


@pytest.mark.parametrize("stop", ["refusal", "max_tokens"])
def test_bad_stop_reason_raises(stop):
    client = FakeClient([FakeResponse(parsed_output=_ticket(), stop_reason=stop)])
    with pytest.raises(ClassificationError):
        classify_ticket("בדיקה", client)


def test_missing_parsed_output_raises():
    client = FakeClient([FakeResponse(parsed_output=None)])
    with pytest.raises(ClassificationError):
        classify_ticket("בדיקה", client)


def test_empty_ticket_does_not_call_the_api():
    client = FakeClient([])
    with pytest.raises(ValueError):
        classify_ticket("  ", client)
    assert client.messages.calls == []
