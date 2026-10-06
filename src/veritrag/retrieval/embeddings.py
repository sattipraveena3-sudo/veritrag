from __future__ import annotations

from typing import Protocol

import numpy as np
from numpy.typing import NDArray
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.preprocessing import normalize

FloatMatrix = NDArray[np.float64]


class EmbeddingBackend(Protocol):
    def encode(self, texts: list[str]) -> FloatMatrix:
        """Encode a batch of texts into L2-normalized vectors."""
        ...


class HashingEmbeddingBackend:
    """Stateless local embedding backend suitable for fast, reproducible demos and CI."""

    def __init__(self, dimensions: int = 2048) -> None:
        self._vectorizer = HashingVectorizer(
            n_features=dimensions,
            alternate_sign=False,
            norm=None,
            ngram_range=(1, 2),
            stop_words="english",
        )

    def encode(self, texts: list[str]) -> FloatMatrix:
        if not texts:
            return np.empty((0, self._vectorizer.n_features), dtype=np.float64)
        matrix = self._vectorizer.transform(texts)
        matrix = normalize(matrix, norm="l2", axis=1)
        return np.asarray(matrix.toarray(), dtype=np.float64)


class SentenceTransformerBackend:
    """Optional dense semantic backend. Install with `pip install -e '.[semantic]'`."""

    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dependency path
            raise RuntimeError(
                "sentence-transformers is not installed; install VeriRAG with [semantic]"
            ) from exc
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> FloatMatrix:
        vectors = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vectors, dtype=np.float64)


def cosine_similarity(query: FloatMatrix, matrix: FloatMatrix) -> NDArray[np.float64]:
    if query.shape[0] != 1:
        raise ValueError("Query matrix must contain exactly one vector")
    if matrix.size == 0:
        return np.empty((0,), dtype=np.float64)
    return matrix @ query[0]
