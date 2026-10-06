from __future__ import annotations

from veritrag.models import SearchHit, SearchOut
from veritrag.retrieval.hybrid import HybridRetriever
from veritrag.storage.sqlite import SQLiteRepository


class SearchService:
    def __init__(self, repository: SQLiteRepository, retriever: HybridRetriever) -> None:
        self.repository = repository
        self.retriever = retriever

    def search(self, query: str, top_k: int) -> SearchOut:
        chunks = self.repository.list_chunks()
        ranked = self.retriever.rank(query, [chunk.text for chunk in chunks], top_k)
        hits = [
            SearchHit(
                chunk_id=chunks[item.index].chunk_id,
                document_id=chunks[item.index].document_id,
                source_id=chunks[item.index].source_id,
                title=chunks[item.index].title,
                text=chunks[item.index].text,
                score=item.score,
                bm25_score=item.bm25_score,
                semantic_score=item.semantic_score,
            )
            for item in ranked
        ]
        return SearchOut(query=query, hits=hits)
