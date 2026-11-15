"""Exercise 2.6 - A complete mini RAG: permissions, citations, "not found".
Task: EXERCISES.md, section 2.6.  Builds on 2.1-2.4.

Run the tests:   pytest 02-rag/tests/test_ex06_mini_rag.py
Try it for real: python 02-rag/run_live.py   (needs ANTHROPIC_API_KEY)
Ask for review:  /review 2.6
"""
from __future__ import annotations

import re  # noqa: F401
from dataclasses import dataclass

from common.embeddings import HashingEmbedder

MODEL = "claude-opus-5-5"
NOT_FOUND = "לא מצאתי את התשובה במסמכים שיש לך גישה אליהם."


@dataclass(frozen=True)
class Document:
    doc_id: str
    department: str   # who may read it, e.g. "hr", "it", "finance", "all"
    text: str         # markdown


@dataclass(frozen=True)
class Answer:
    text: str
    citations: list[str]   # chunk ids that the answer cites and that were really provided
    used_chunks: list[str]  # chunk ids that were sent to the model (empty if not found)


SYSTEM_PROMPT = """
"""  # TODO: answer only from the sources, cite as [n], say NOT_FOUND text when the answer is missing


class MiniRAG:
    def __init__(self, documents: list[Document], *, embedder=None, max_chars: int = 600,
                 overlap: int = 100, min_score: float = 0.25):
        """Index everything once: chunk all docs, remember each chunk's department,
        embed all chunks (one matrix), build BM25 over tokenized chunks."""
        self.embedder = embedder or HashingEmbedder()
        self.min_score = min_score
        raise NotImplementedError

    def retrieve(self, question: str, departments: set[str], top_k: int = 4) -> list[tuple[object, float]]:
        """Hybrid retrieval restricted to chunks whose department is in `departments`
        or is "all". Return [(Chunk, best cosine score of that chunk)] best first.
        Permission filtering must happen BEFORE ranking, not after."""
        raise NotImplementedError

    def build_prompt(self, question: str, chunks: list) -> str:
        """User message: numbered sources then the question, e.g.

        <sources>
        <source n="1" id="hr-leave#0" heading="...">...</source>
        ...
        </sources>
        <question>...</question>
        """
        raise NotImplementedError

    def answer(self, question: str, departments: set[str], client, model: str = MODEL) -> Answer:
        """1. retrieve; 2. if nothing retrieved or best cosine < min_score -> return
        Answer(NOT_FOUND, [], []) WITHOUT calling the model; 3. call the model;
        4. map [n] markers in the reply back to chunk ids, dropping invalid n."""
        raise NotImplementedError
