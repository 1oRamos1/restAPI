import json
import os

import pytest

from common.fakes import FakeClient, FakeResponse, text_block
from ex06_mini_rag import NOT_FOUND, SYSTEM_PROMPT, Answer, Document, MiniRAG

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def load_docs():
    meta = json.load(open(os.path.join(DATA, "docs.json"), encoding="utf-8"))
    return [Document(m["doc_id"], m["department"],
                     open(os.path.join(DATA, m["path"]), encoding="utf-8").read()) for m in meta]


@pytest.fixture(scope="module")
def rag():
    return MiniRAG(load_docs())


def test_system_prompt_rules():
    sp = SYSTEM_PROMPT
    assert len(sp.strip()) > 200
    assert NOT_FOUND in sp, "tell the model the exact not-found sentence"
    assert "[" in sp, "explain the [n] citation format"


def test_retrieve_relevant_chunk(rag):
    res = rag.retrieve("כמה ימי מחלה מגיעים לעובד בשנה?", {"hr"})
    assert res and any("18 ימי מחלה" in c.text for c, _ in res)
    scores = [s for _, s in res]
    assert scores == sorted(scores, reverse=True)


def test_permissions_filter(rag):
    res = rag.retrieve("כמה ימי מחלה מגיעים לעובד בשנה?", {"it"})
    assert all(c.doc_id != "hr-leave" for c, _ in res)
    res = rag.retrieve("עד מתי מגישים קבלות?", {"hr"})
    assert all(c.doc_id != "finance-expenses" for c, _ in res)


def test_department_all_is_visible_to_everyone(rag):
    res = rag.retrieve("מה עושים בשגיאה VPN-809?", {"finance"})
    assert any(c.doc_id == "it-vpn" for c, _ in res)


def test_build_prompt_numbers_sources(rag):
    chunks = [c for c, _ in rag.retrieve("ימי מחלה", {"hr"}, top_k=2)]
    p = rag.build_prompt("כמה ימי מחלה?", chunks)
    assert '<source n="1"' in p and '<source n="2"' in p
    assert f'id="{chunks[0].id}"' in p
    assert "<question>" in p and "כמה ימי מחלה?" in p
    assert p.index("<sources>") < p.index("<question>")


def test_answer_maps_citations(rag):
    client = FakeClient([FakeResponse(content=[text_block("מגיעים 18 ימי מחלה בשנה [1]. ראו גם [9].")])])
    ans = rag.answer("כמה ימי מחלה מגיעים לעובד בשנה?", {"hr"}, client)
    assert isinstance(ans, Answer)
    assert len(client.messages.calls) == 1
    call = client.messages.calls[0]
    assert call["system"] == SYSTEM_PROMPT
    assert ans.citations == [ans.used_chunks[0]], "[1] maps to the first source, [9] is dropped"
    assert "18" in ans.text


def test_answer_dedupes_citations(rag):
    client = FakeClient([FakeResponse(content=[text_block("א [2] ב [1] ג [2]")])])
    ans = rag.answer("כמה ימי מחלה מגיעים לעובד בשנה?", {"hr"}, client)
    assert ans.citations == [ans.used_chunks[1], ans.used_chunks[0]]


def test_not_found_skips_model(rag):
    client = FakeClient([])
    ans = rag.answer("מה מזג האוויר בטוקיו מחר?", {"hr"}, client)
    assert ans.text == NOT_FOUND and ans.citations == [] and ans.used_chunks == []
    assert client.messages.calls == []


def test_no_permission_means_not_found(rag):
    client = FakeClient([])
    ans = rag.answer("עד מתי מגישים קבלות להחזר הוצאות?", {"marketing"}, client)
    assert ans.text == NOT_FOUND
    assert client.messages.calls == []
