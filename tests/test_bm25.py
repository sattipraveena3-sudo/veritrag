from veritrag.retrieval.bm25 import BM25Index


def test_bm25_prefers_matching_document() -> None:
    docs = ["cats sleep on sofas", "postgres supports transactional workloads"]
    scores = BM25Index(docs).scores("postgres transaction")
    assert scores[1] > scores[0]
