from veritrag.core.text import chunk_text, split_claims


def test_chunk_text_respects_overlap_and_content() -> None:
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa"
    chunks = chunk_text(text, chunk_size=25, overlap=5)
    assert len(chunks) >= 2
    assert "alpha" in chunks[0]
    assert "kappa" in chunks[-1]


def test_split_claims_returns_multiple_claims() -> None:
    claims = split_claims("The plan is active. It includes 24/7 support.")
    assert claims == ["The plan is active.", "It includes 24/7 support."]
