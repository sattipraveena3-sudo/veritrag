from veritrag.config import Settings
from veritrag.container import build_container
from veritrag.models import AuditIn, DocumentIn


def test_supported_answer_passes_audit() -> None:
    settings = Settings(
        db_path=":memory:",
        chunk_size=500,
        chunk_overlap=50,
        min_support_score=0.25,
        max_risk_score=0.65,
    )
    container = build_container(settings)
    try:
        container.indexing.ingest(
            DocumentIn(
                source_id="policy",
                title="Policy",
                text=(
                    "Enterprise support targets a one-hour response time "
                    "for priority-one incidents."
                ),
            )
        )
        result = container.audit.audit(
            AuditIn(
                question="What is the Enterprise priority-one response time?",
                answer=(
                    "Enterprise support targets a one-hour response time "
                    "for priority-one incidents."
                ),
            )
        )
        assert result.passed is True
        assert result.supported_claim_ratio == 1.0
        assert result.claims[0].status == "supported"
    finally:
        container.repository.close()


def test_unsupported_answer_fails_audit() -> None:
    settings = Settings(
        db_path=":memory:",
        chunk_size=500,
        chunk_overlap=50,
        min_support_score=0.55,
        max_risk_score=0.45,
    )
    container = build_container(settings)
    try:
        container.indexing.ingest(
            DocumentIn(
                source_id="policy",
                title="Policy",
                text=(
                    "Enterprise support targets a one-hour response time "
                    "for priority-one incidents."
                ),
            )
        )
        result = container.audit.audit(
            AuditIn(
                question="What is the Enterprise priority-one response time?",
                answer="Enterprise support guarantees a five-minute response for every incident.",
            )
        )
        assert result.passed is False
    finally:
        container.repository.close()


def test_default_threshold_handles_multi_sentence_evidence_and_numeric_contradiction() -> None:
    settings = Settings(db_path=":memory:")
    container = build_container(settings)
    try:
        container.indexing.ingest(
            DocumentIn(
                source_id="support-policy",
                title="Support Policy",
                text=(
                    "Starter support provides email support during business hours. "
                    "Business support targets four hours for priority-one incidents. "
                    "Enterprise support provides 24/7 phone, chat, and email support with "
                    "a one-hour target response time for priority-one incidents. "
                    "Production API rate limits are 2,000 requests per minute for "
                    "Enterprise accounts."
                ),
            )
        )

        supported = container.audit.audit(
            AuditIn(
                question="What is the Enterprise priority-one response time?",
                answer=(
                    "Enterprise support targets a one-hour response time "
                    "for priority-one incidents."
                ),
            )
        )
        contradicted = container.audit.audit(
            AuditIn(
                question="What is the Enterprise priority-one response time?",
                answer=(
                    "Enterprise support targets a ten-minute response time "
                    "for priority-one incidents."
                ),
            )
        )

        assert supported.passed is True
        assert supported.claims[0].status == "supported"
        assert contradicted.passed is False
        assert contradicted.claims[0].status == "unsupported"
        assert "numeric_fact_mismatch_penalty" in contradicted.claims[0].reasons
    finally:
        container.repository.close()
