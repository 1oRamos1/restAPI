"""A tiny deterministic embedder for offline exercises.

It is NOT semantic: it hashes words (and character trigrams) into a fixed-size
vector. That is enough to practise the vector-search plumbing without an API
key. In the real project you swap it for a real multilingual embedding model
(Bedrock Titan / Cohere / Voyage / OpenAI ...) behind the same `embed()` API.
"""
from __future__ import annotations

import hashlib
import re

import numpy as np

_WORD = re.compile(r"\w+", re.UNICODE)


class HashingEmbedder:
    def __init__(self, dim: int = 512):
        self.dim = dim

    def _features(self, text: str) -> list[str]:
        words = [w.lower() for w in _WORD.findall(text)]
        feats = list(words)
        for w in words:
            padded = f"#{w}#"
            feats += [padded[i : i + 3] for i in range(len(padded) - 2)]
        return feats

    def embed(self, text: str) -> np.ndarray:
        v = np.zeros(self.dim, dtype=np.float32)
        for f in self._features(text):
            h = int.from_bytes(hashlib.md5(f.encode("utf-8")).digest()[:4], "little")
            v[h % self.dim] += 1.0 if (h >> 31) & 1 else -1.0
        n = np.linalg.norm(v)
        return v / n if n else v

    def embed_many(self, texts: list[str]) -> np.ndarray:
        return np.vstack([self.embed(t) for t in texts]) if texts else np.zeros((0, self.dim), dtype=np.float32)
