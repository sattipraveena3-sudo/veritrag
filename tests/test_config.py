from veritrag.config import Settings


def test_settings_from_env_uses_defaults(monkeypatch) -> None:
    for name in (
        "VERITRAG_DB_PATH",
        "VERITRAG_EMBEDDING_BACKEND",
        "VERITRAG_SENTENCE_MODEL",
        "VERITRAG_CHUNK_SIZE",
        "VERITRAG_CHUNK_OVERLAP",
        "VERITRAG_MIN_SUPPORT_SCORE",
        "VERITRAG_MAX_RISK_SCORE",
    ):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_env()
    assert settings.db_path == "./veritrag.db"
    assert settings.chunk_size == 900
    assert settings.chunk_overlap == 120
