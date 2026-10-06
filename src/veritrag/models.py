from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DocumentIn(BaseModel):
    source_id: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=300)
    text: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentOut(BaseModel):
    document_id: str
    source_id: str
    title: str
    chunk_count: int


class SearchIn(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    chunk_id: str
    document_id: str
    source_id: str
    title: str
    text: str
    score: float
    bm25_score: float
    semantic_score: float


class SearchOut(BaseModel):
    query: str
    hits: list[SearchHit]


class AuditIn(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    top_k: int = Field(default=6, ge=1, le=20)


class ClaimResult(BaseModel):
    claim: str
    support_score: float
    status: str
    evidence_chunk_id: str | None
    evidence_text: str | None
    reasons: list[str]


class AuditOut(BaseModel):
    audit_id: str
    question: str
    answer: str
    risk_score: float
    passed: bool
    retrieval_confidence: float
    supported_claim_ratio: float
    claims: list[ClaimResult]
    evidence: list[SearchHit]
