"""Ask your MiniRAG (ex06) real questions with a real model.

    export ANTHROPIC_API_KEY=...      (or a .env file - never commit it)
    python 02-rag/run_live.py
"""
import json
import os
import sys

HERE = os.path.dirname(__file__)
sys.path[:0] = [HERE, os.path.dirname(HERE)]

import anthropic  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from ex06_mini_rag import Document, MiniRAG  # noqa: E402

meta = json.load(open(os.path.join(HERE, "data", "docs.json"), encoding="utf-8"))
docs = [Document(m["doc_id"], m["department"],
                 open(os.path.join(HERE, "data", m["path"]), encoding="utf-8").read()) for m in meta]
rag = MiniRAG(docs)
client = anthropic.Anthropic()

QUESTIONS = [
    ("כמה ימי מחלה מגיעים לי, וכמה מהם משולמים?", {"hr"}),
    ("מה עושים כשמופיעה שגיאה VPN-809?", {"finance"}),
    ("עד מתי אפשר להגיש קבלות?", {"finance"}),
    ("עד מתי אפשר להגיש קבלות?", {"marketing"}),      # no permission
    ("מה שעות הפעילות של חדר הכושר?", {"hr"}),         # not in the documents
]

for q, depts in QUESTIONS:
    ans = rag.answer(q, depts, client)
    print(f"\n> {q}   (departments={sorted(depts)})\n{ans.text}\n  citations: {ans.citations}")
