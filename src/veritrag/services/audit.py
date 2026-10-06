from __future__ import annotations

from veritrag.core.risk import compute_risk
from veritrag.core.text import split_claims
from veritrag.core.verification import ClaimVerifier
from veritrag.models import AuditIn, AuditOut, ClaimResult
from veritrag.services.search import SearchService
from veritrag.storage.sqlite import SQLiteRepository


class AuditService:
    def __init__(
        self,
        repository: SQLiteRepository,
        search_service: SearchService,
        verifier: ClaimVerifier,
        max_risk_score: float,
    ) -> None:
        self.repository = repository
        self.search_service = search_service
        self.verifier = verifier
        self.max_risk_score = max_risk_score

    def audit(self, request: AuditIn) -> AuditOut:
        evidence = self.search_service.search(request.question, request.top_k).hits
        retrieval_confidence = (
            sum(hit.score for hit in evidence[:3]) / min(len(evidence), 3)
            if evidence
            else 0.0
        )
        claims = split_claims(request.answer)
        evidence_texts = [hit.text for hit in evidence]
        verification = [self.verifier.verify(claim, evidence_texts) for claim in claims]
        risk = compute_risk(
            verification,
            retrieval_confidence,
            max_risk_score=self.max_risk_score,
        )

        claim_results: list[ClaimResult] = []
        for claim, result in zip(claims, verification, strict=True):
            selected = (
                evidence[result.evidence_index]
                if result.evidence_index is not None
                else None
            )
            claim_results.append(
                ClaimResult(
                    claim=claim,
                    support_score=result.support_score,
                    status=result.status,
                    evidence_chunk_id=selected.chunk_id if selected else None,
                    evidence_text=selected.text if selected else None,
                    reasons=result.reasons,
                )
            )

        payload = {
            "question": request.question,
            "answer": request.answer,
            "risk_score": risk.risk_score,
            "passed": risk.passed,
            "retrieval_confidence": retrieval_confidence,
            "supported_claim_ratio": risk.supported_claim_ratio,
            "claims": [claim.model_dump() for claim in claim_results],
            "evidence": [hit.model_dump() for hit in evidence],
        }
        audit_id = self.repository.save_audit(payload)
        return AuditOut(audit_id=audit_id, **payload)
