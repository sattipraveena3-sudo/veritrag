from __future__ import annotations

import math
from collections import Counter

from veritrag.core.text import tokenize


class BM25Index:
    def __init__(self, documents: list[str], *, k1: float = 1.5, b: float = 0.75) -> None:
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.tokens = [tokenize(doc) for doc in documents]
        self.doc_freq: Counter[str] = Counter()
        for tokens in self.tokens:
            self.doc_freq.update(set(tokens))
        self.avg_doc_len = (
            sum(len(tokens) for tokens in self.tokens) / len(self.tokens) if self.tokens else 0.0
        )

    def scores(self, query: str) -> list[float]:
        if not self.documents:
            return []
        query_terms = tokenize(query)
        n_docs = len(self.documents)
        scores: list[float] = []
        for tokens in self.tokens:
            tf = Counter(tokens)
            doc_len = len(tokens)
            score = 0.0
            for term in query_terms:
                frequency = tf.get(term, 0)
                if frequency == 0:
                    continue
                df = self.doc_freq.get(term, 0)
                idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
                length_norm = 1 - self.b + self.b * doc_len / max(self.avg_doc_len, 1.0)
                numerator = frequency * (self.k1 + 1)
                denominator = frequency + self.k1 * length_norm
                score += idf * numerator / denominator
            scores.append(score)
        return scores
