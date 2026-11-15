"""Exercise 2.1 - Structure-aware chunking.  Task: EXERCISES.md, section 2.1

Run the tests:   pytest 02-rag/tests/test_ex01_chunking.py
Ask for review:  /review 2.1
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    id: str          # f"{doc_id}#{index}"  - stable and unique
    doc_id: str
    index: int       # position of the chunk inside the document, from 0
    heading: str     # the section heading this chunk belongs to ("" before the first heading)
    text: str


def split_sections(markdown: str) -> list[tuple[str, str]]:
    """Split a markdown document into (heading, body) pairs.

    A heading is a line starting with one or more '#' followed by a space.
    The heading text is stored without the '#' marks. Text before the first
    heading gets heading "". Empty sections (no body text) are skipped.
    """
    raise NotImplementedError


def chunk_document(markdown: str, doc_id: str, *, max_chars: int = 800, overlap: int = 150) -> list[Chunk]:
    """Chunk a document. Rules:

    1. Chunks never cross a section boundary.
    2. Inside a section, pack whole paragraphs (separated by blank lines) until
       the next one would exceed max_chars.
    3. A paragraph longer than max_chars is split on sentence ends (. ! ? or newline);
       a single sentence longer than max_chars is hard-split.
    4. Consecutive chunks of the same section overlap: a new chunk starts with
       up to `overlap` characters from the end of the previous chunk.
    5. Every chunk is at most max_chars long (overlap included) and not empty.
    6. Raise ValueError if overlap >= max_chars or max_chars <= 0.
    """
    raise NotImplementedError
