from __future__ import annotations

import re
from collections.abc import Iterable

_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_'-]*")


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in _TOKEN.finditer(text)]


def split_claims(answer: str) -> list[str]:
    clean = normalize_whitespace(answer)
    if not clean:
        return []
    parts = [part.strip(" -•\t") for part in _SENTENCE_BOUNDARY.split(clean)]
    claims = [part for part in parts if len(tokenize(part)) >= 3]
    return claims or [clean]


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    clean = normalize_whitespace(text)
    if not clean:
        return []
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunking configuration")

    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        if end < len(clean):
            boundary = clean.rfind(" ", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk = clean[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(clean):
            break
        start = max(0, end - overlap)
    return chunks


def jaccard_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)
