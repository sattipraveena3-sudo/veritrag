from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from veritrag.retrieval.bm25 import BM25Index
from veritrag.retrieval.embeddings import EmbeddingBackend, cosine_similarity


@dataclass(frozen=True, slots=True)
class RankedChunk:
    index: int
    score: float
    bm25_score: float
    semantic_score: float


def _minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    low, high = min(values), max(values)
    if high - low < 1e-12:
        return [1.0 if high > 0 else 0.0 for _ in values]
    return [(value - low) / (high - low) for value in values]


class HybridRetriever:
    def __init__(self, embedder: EmbeddingBackend, *, semantic_weight: float = 0.55) -> None:
        if not 0 <= semantic_weight <= 1:
            raise ValueError("semantic_weight must be in [0, 1]")
        self.embedder = embedder
        self.semantic_weight = semantic_weight

    def rank(self, query: str, texts: list[str], top_k: int) -> list[RankedChunk]:
        if not texts:
            return []
        bm25_raw = BM25Index(texts).scores(query)
        doc_vectors = self.embedder.encode(texts)
        query_vector = self.embedder.encode([query])
        semantic_raw = cosine_similarity(query_vector, doc_vectors).tolist()
        bm25 = _minmax(bm25_raw)
        semantic = [float(np.clip(value, 0.0, 1.0)) for value in semantic_raw]

        ranked: list[RankedChunk] = []
        for index in range(len(texts)):
            score = (
                (1 - self.semantic_weight) * bm25[index]
                + self.semantic_weight * semantic[index]
            )
            ranked.append(
                RankedChunk(
                    index=index,
                    score=float(score),
                    bm25_score=float(bm25[index]),
                    semantic_score=float(semantic[index]),
                )
            )
        ranked.sort(key=lambda item: item.score, reverse=True)
        return ranked[:top_k]
