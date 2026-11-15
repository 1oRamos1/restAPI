import os

import pytest

from ex01_chunking import Chunk, chunk_document, split_sections

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
HR = open(os.path.join(DATA, "hr-leave.md"), encoding="utf-8").read()


def test_split_sections_headings_and_preamble():
    md = "מבוא קצר\n\n# כותרת א\nגוף א\n\n## כותרת ב\nגוף ב\n# ריקה\n\n"
    assert split_sections(md) == [("", "מבוא קצר"), ("כותרת א", "גוף א"), ("כותרת ב", "גוף ב")]


def test_hash_without_space_is_not_heading():
    md = "# כותרת\nמספר #5 בתור\n#לא_כותרת"
    secs = split_sections(md)
    assert len(secs) == 1 and "#לא_כותרת" in secs[0][1]


def test_real_document_sections():
    heads = [h for h, _ in split_sections(HR)]
    assert heads == ["נוהל חופשות והיעדרויות", "צבירת ימי חופשה", "בקשת חופשה", "ימי מחלה"]


def test_chunks_respect_max_and_are_not_empty():
    for max_chars, overlap in [(800, 150), (300, 50), (120, 30)]:
        chunks = chunk_document(HR, "hr", max_chars=max_chars, overlap=overlap)
        assert chunks
        assert all(0 < len(c.text) <= max_chars for c in chunks), (max_chars, overlap)


def test_ids_are_stable_and_unique():
    a = chunk_document(HR, "hr", max_chars=300, overlap=50)
    b = chunk_document(HR, "hr", max_chars=300, overlap=50)
    assert [c.id for c in a] == [c.id for c in b]
    assert len({c.id for c in a}) == len(a)
    assert [c.index for c in a] == list(range(len(a)))
    assert all(c.id == f"hr#{c.index}" and c.doc_id == "hr" for c in a)
    assert all(isinstance(c, Chunk) for c in a)


def test_chunks_do_not_cross_sections():
    chunks = chunk_document(HR, "hr", max_chars=300, overlap=50)
    sick = [c for c in chunks if c.heading == "ימי מחלה"]
    assert sick and all("טופס HR-114" not in c.text for c in sick)
    assert all("ימי מחלה" not in c.text or c.heading == "ימי מחלה" for c in chunks if "18 ימי מחלה" in c.text)


def test_every_sentence_is_covered():
    chunks = chunk_document(HR, "hr", max_chars=200, overlap=40)
    joined = "\n".join(c.text for c in chunks)
    for sentence in ["ניתן לצבור עד 40 ימים", "בטופס HR-114", "תוך שבעה ימים"]:
        assert sentence in joined


def test_small_sections_become_one_chunk_each():
    md = "# א\nפסקה אחת.\n\nפסקה שתיים.\n\n# ב\nעוד פסקה."
    chunks = chunk_document(md, "d", max_chars=500, overlap=50)
    assert [(c.heading, c.text) for c in chunks] == [("א", "פסקה אחת.\n\nפסקה שתיים."), ("ב", "עוד פסקה.")]


def test_overlap_between_consecutive_chunks_of_same_section():
    para = " ".join(f"משפט מספר {i} בפסקה הארוכה." for i in range(40))
    chunks = chunk_document(f"# ארוך\n{para}", "d", max_chars=200, overlap=60)
    assert len(chunks) > 2
    for prev, nxt in zip(chunks, chunks[1:]):
        tail = prev.text[-20:]
        assert tail in nxt.text[:80], "next chunk should start with the end of the previous one"


def test_huge_sentence_is_hard_split():
    md = "# x\n" + "א" * 1000
    chunks = chunk_document(md, "d", max_chars=300, overlap=0)
    assert all(len(c.text) <= 300 for c in chunks)
    assert sum(len(c.text) for c in chunks) == 1000


@pytest.mark.parametrize("max_chars,overlap", [(100, 100), (100, 150), (0, 0)])
def test_invalid_params(max_chars, overlap):
    with pytest.raises(ValueError):
        chunk_document("# a\nb", "d", max_chars=max_chars, overlap=overlap)
