from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np

from veritrag.core.text import jaccard_similarity, split_claims, tokenize
from veritrag.retrieval.embeddings import EmbeddingBackend, cosine_similarity

_NEGATIONS = {"no", "not", "never", "none", "without", "cannot", "can't", "isn't", "wasn't"}
_NUMBER_WORDS = {
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
    "hundred",
    "thousand",
    "million",
}
_NUMERIC_PREFIX = re.compile(r"^\d")


@dataclass(frozen=True, slots=True)
class VerificationResult:
    support_score: float
    status: str
    evidence_index: int | None
    reasons: list[str]


def _negation_mismatch(claim: str, evidence: str) -> bool:
    claim_tokens = set(tokenize(claim))
    evidence_tokens = set(tokenize(evidence))
    return bool(claim_tokens & _NEGATIONS) != bool(evidence_tokens & _NEGATIONS)


def _fact_tokens(text: str) -> set[str]:
    """Extract compact factual anchors that should not silently change.

    Numeric values and number-bearing compounds (for example ``one-hour`` or ``600``)
    are intentionally treated as hard anchors. This keeps high lexical similarity from
    accepting a claim whose quantity differs from the evidence.
    """

    facts: set[str] = set()
    for token in tokenize(text):
        if _NUMERIC_PREFIX.match(token):
            facts.add(token)
            continue
        head = token.split("-", 1)[0]
        if token in _NUMBER_WORDS or head in _NUMBER_WORDS:
            facts.add(token)
    return facts


def _fact_mismatch(claim: str, evidence: str) -> bool:
    claim_facts = _fact_tokens(claim)
    if not claim_facts:
        return False
    evidence_facts = _fact_tokens(evidence)
    return not claim_facts.issubset(evidence_facts)


class ClaimVerifier:
    def __init__(self, embedder: EmbeddingBackend, min_support_score: float) -> None:
        self.embedder = embedder
        self.min_support_score = min_support_score

    def verify(self, claim: str, evidence: list[str]) -> VerificationResult:
        if not evidence:
            return VerificationResult(0.0, "unsupported", None, ["No evidence was retrieved"])

        candidates: list[tuple[int, str]] = []
        for chunk_index, chunk in enumerate(evidence):
            sentences = split_claims(chunk)
            if not sentences:
                sentences = [chunk]
            candidates.extend((chunk_index, sentence) for sentence in sentences)

        claim_vector = self.embedder.encode([claim])
        candidate_vectors = self.embedder.encode([sentence for _, sentence in candidates])
        semantic_scores = cosine_similarity(claim_vector, candidate_vectors)

        best_chunk_index: int | None = None
        best_score = -1.0
        best_reasons: list[str] = []

        for candidate_index, (chunk_index, sentence) in enumerate(candidates):
            semantic = float(np.clip(semantic_scores[candidate_index], 0.0, 1.0))
            lexical = jaccard_similarity(tokenize(claim), tokenize(sentence))
            score = 0.72 * semantic + 0.28 * lexical
            reasons = [
                f"semantic_similarity={semantic:.3f}",
                f"lexical_overlap={lexical:.3f}",
                f"matched_sentence={sentence}",
            ]
            if _negation_mismatch(claim, sentence):
                score *= 0.65
                reasons.append("negation_mismatch_penalty")
            if _fact_mismatch(claim, sentence):
                score *= 0.35
                reasons.append("numeric_fact_mismatch_penalty")
            if score > best_score:
                best_score = score
                best_chunk_index = chunk_index
                best_reasons = reasons

        bounded = float(np.clip(best_score, 0.0, 1.0))
        status = "supported" if bounded >= self.min_support_score else "unsupported"
        return VerificationResult(bounded, status, best_chunk_index, best_reasons)
