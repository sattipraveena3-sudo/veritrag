from veritrag.retrieval.embeddings import HashingEmbeddingBackend
from veritrag.retrieval.hybrid import HybridRetriever


def test_hybrid_retriever_ranks_relevant_text_first() -> None:
    retriever = HybridRetriever(HashingEmbeddingBackend())
    texts = [
        "The enterprise plan has a one hour incident response target.",
        "The office cafeteria serves lunch at noon.",
    ]
    result = retriever.rank("enterprise incident response", texts, top_k=2)
    assert result[0].index == 0
    assert result[0].score >= result[1].score
