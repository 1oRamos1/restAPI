import math

import pytest

from ex03_bm25 import BM25, tokenize


def test_tokenize_basic():
    assert tokenize("שלום, World! VPN-809") == ["שלום", "world", "vpn", "809"]


def test_tokenize_hebrew_prefixes():
    assert tokenize("והחזר בחשבון דוח של רפואי", strip_hebrew_prefix=True) == ["החזר", "חשבון", "דוח", "של", "רפואי"]
    # short words and non-Hebrew are untouched
    assert tokenize("בית VPN", strip_hebrew_prefix=True) == ["בית", "vpn"]


def test_naive_prefix_rule_has_false_positives():
    # Known limitation, by design of the spec: "כספים" (money) is not "כ" + "ספים".
    # Think about it for the review: what does this do to recall and precision?
    assert tokenize("כספים לקוח", strip_hebrew_prefix=True) == ["ספים", "קוח"]


DOCS = [
    "חופשה שנתית ימי חופשה".split(),
    "ימי מחלה ואישור רפואי".split(),
    "vpn שגיאה 809 חומת אש".split(),
    "חופשה".split(),
]


def test_idf_formula():
    bm = BM25(DOCS)
    n, df = 4, 2  # "חופשה" appears in docs 0 and 3
    assert bm.idf("חופשה") == pytest.approx(math.log((n - df + 0.5) / (df + 0.5) + 1))
    assert bm.idf("לא-קיים") > bm.idf("חופשה")


def test_scores_exact_formula_single_term():
    bm = BM25(DOCS, k1=1.5, b=0.75)
    avgdl = sum(len(d) for d in DOCS) / len(DOCS)
    tf, dl = 2, len(DOCS[0])
    expected = bm.idf("חופשה") * tf * 2.5 / (tf + 1.5 * (1 - 0.75 + 0.75 * dl / avgdl))
    assert bm.scores(["חופשה"])[0] == pytest.approx(expected)


def test_rare_exact_term_wins():
    bm = BM25(DOCS)
    assert bm.top_k(["809"], k=3)[0][0] == 2
    assert [i for i, _ in bm.top_k(["809"], k=3)] == [2], "only docs with score > 0"


def test_length_normalisation_prefers_short_doc():
    bm = BM25(DOCS)
    s = bm.scores(["חופשה"])
    assert s[3] > 0 and s[0] > 0
    # doc 3 is just "חופשה" - with tf=1 it should beat a long doc with the same tf
    long_doc = BM25([["חופשה"] + ["מילה"] * 20, ["חופשה"], ["אחר"]])
    s2 = long_doc.scores(["חופשה"])
    assert s2[1] > s2[0]


def test_repeated_query_terms_count_once():
    bm = BM25(DOCS)
    assert bm.scores(["חופשה", "חופשה"]) == pytest.approx(bm.scores(["חופשה"]))


def test_unknown_terms_score_zero():
    bm = BM25(DOCS)
    assert bm.scores(["אין"]) == [0.0] * 4
    assert bm.top_k(["אין"], k=2) == []
