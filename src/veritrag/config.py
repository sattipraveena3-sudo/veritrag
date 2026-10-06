from __future__ import annotations

import os
from dataclasses import dataclass

_DEFAULT_DB_PATH = "./veritrag.db"
_DEFAULT_EMBEDDING_BACKEND = "hashing"
_DEFAULT_SENTENCE_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_DEFAULT_CHUNK_SIZE = 900
_DEFAULT_CHUNK_OVERLAP = 120
_DEFAULT_MIN_SUPPORT_SCORE = 0.48
_DEFAULT_MAX_RISK_SCORE = 0.45


@dataclass(frozen=True, slots=True)
class Settings:
    db_path: str = _DEFAULT_DB_PATH
    embedding_backend: str = _DEFAULT_EMBEDDING_BACKEND
    sentence_model: str = _DEFAULT_SENTENCE_MODEL
    chunk_size: int = _DEFAULT_CHUNK_SIZE
    chunk_overlap: int = _DEFAULT_CHUNK_OVERLAP
    min_support_score: float = _DEFAULT_MIN_SUPPORT_SCORE
    max_risk_score: float = _DEFAULT_MAX_RISK_SCORE

    @classmethod
    def from_env(cls) -> "Settings":
        settings = cls(
            db_path=os.getenv("VERITRAG_DB_PATH", _DEFAULT_DB_PATH),
            embedding_backend=os.getenv(
                "VERITRAG_EMBEDDING_BACKEND", _DEFAULT_EMBEDDING_BACKEND
            ),
            sentence_model=os.getenv("VERITRAG_SENTENCE_MODEL", _DEFAULT_SENTENCE_MODEL),
            chunk_size=int(os.getenv("VERITRAG_CHUNK_SIZE", str(_DEFAULT_CHUNK_SIZE))),
            chunk_overlap=int(
                os.getenv("VERITRAG_CHUNK_OVERLAP", str(_DEFAULT_CHUNK_OVERLAP))
            ),
            min_support_score=float(
                os.getenv("VERITRAG_MIN_SUPPORT_SCORE", str(_DEFAULT_MIN_SUPPORT_SCORE))
            ),
            max_risk_score=float(
                os.getenv("VERITRAG_MAX_RISK_SCORE", str(_DEFAULT_MAX_RISK_SCORE))
            ),
        )
        if settings.chunk_overlap >= settings.chunk_size:
            raise ValueError("VERITRAG_CHUNK_OVERLAP must be smaller than VERITRAG_CHUNK_SIZE")
        if not 0 <= settings.min_support_score <= 1:
            raise ValueError("VERITRAG_MIN_SUPPORT_SCORE must be in [0, 1]")
        if not 0 <= settings.max_risk_score <= 1:
            raise ValueError("VERITRAG_MAX_RISK_SCORE must be in [0, 1]")
        return settings
