from __future__ import annotations

from dataclasses import dataclass

from veritrag.core.verification import VerificationResult


@dataclass(frozen=True, slots=True)
class RiskSummary:
    risk_score: float
    supported_claim_ratio: float
    passed: bool


def compute_risk(
    claims: list[VerificationResult],
    retrieval_confidence: float,
    *,
    max_risk_score: float,
) -> RiskSummary:
    if not claims:
        return RiskSummary(risk_score=1.0, supported_claim_ratio=0.0, passed=False)

    supported = sum(item.status == "supported" for item in claims)
    ratio = supported / len(claims)
    average_support = sum(item.support_score for item in claims) / len(claims)
    retrieval_penalty = 1 - min(max(retrieval_confidence, 0.0), 1.0)
    risk = 0.55 * (1 - ratio) + 0.30 * (1 - average_support) + 0.15 * retrieval_penalty
    risk = min(max(risk, 0.0), 1.0)
    return RiskSummary(
        risk_score=risk,
        supported_claim_ratio=ratio,
        passed=risk <= max_risk_score and ratio == 1.0,
    )
