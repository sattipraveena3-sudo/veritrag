from __future__ import annotations

from veritrag.config import Settings
from veritrag.core.text import chunk_text
from veritrag.models import DocumentIn, DocumentOut
from veritrag.storage.sqlite import SQLiteRepository


class IndexingService:
    def __init__(self, repository: SQLiteRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def ingest(self, document: DocumentIn) -> DocumentOut:
        chunks = chunk_text(
            document.text,
            chunk_size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
        )
        document_id, chunk_count = self.repository.upsert_document(
            source_id=document.source_id,
            title=document.title,
            text=document.text,
            metadata=document.metadata,
            chunks=chunks,
        )
        return DocumentOut(
            document_id=document_id,
            source_id=document.source_id,
            title=document.title,
            chunk_count=chunk_count,
        )
