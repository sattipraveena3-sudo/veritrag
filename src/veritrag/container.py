from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from veritrag.config import Settings
from veritrag.core.verification import ClaimVerifier
from veritrag.retrieval.embeddings import (
    EmbeddingBackend,
    HashingEmbeddingBackend,
    SentenceTransformerBackend,
)
from veritrag.retrieval.hybrid import HybridRetriever
from veritrag.services.audit import AuditService
from veritrag.services.indexing import IndexingService
from veritrag.services.search import SearchService
from veritrag.storage.sqlite import SQLiteRepository


@dataclass(frozen=True, slots=True)
class Container:
    settings: Settings
    repository: SQLiteRepository
    indexing: IndexingService
    search: SearchService
    audit: AuditService


def _make_embedder(settings: Settings) -> EmbeddingBackend:
    if settings.embedding_backend == "hashing":
        return HashingEmbeddingBackend()
    if settings.embedding_backend == "sentence-transformer":
        return SentenceTransformerBackend(settings.sentence_model)
    raise ValueError(f"Unknown embedding backend: {settings.embedding_backend}")


def build_container(settings: Settings | None = None) -> Container:
    resolved = settings or Settings.from_env()
    repository = SQLiteRepository(resolved.db_path)
    embedder = _make_embedder(resolved)
    retriever = HybridRetriever(embedder)
    search = SearchService(repository, retriever)
    indexing = IndexingService(repository, resolved)
    verifier = ClaimVerifier(embedder, resolved.min_support_score)
    audit = AuditService(repository, search, verifier, resolved.max_risk_score)
    return Container(resolved, repository, indexing, search, audit)


@lru_cache(maxsize=1)
def get_container() -> Container:
    return build_container()
