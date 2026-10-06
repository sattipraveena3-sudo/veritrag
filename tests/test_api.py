from fastapi.testclient import TestClient

from veritrag.api.app import app
from veritrag.config import Settings
from veritrag.container import build_container, get_container


def test_health_and_ingestion() -> None:
    test_container = build_container(
        Settings(db_path=":memory:", chunk_size=500, chunk_overlap=50)
    )
    app.dependency_overrides[get_container] = lambda: test_container
    try:
        client = TestClient(app)
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post(
            "/v1/documents",
            json={
                "source_id": "doc-1",
                "title": "Example",
                "text": "A sufficiently long sentence about a production system and its policy.",
            },
        )
        assert response.status_code == 201
        assert response.json()["chunk_count"] == 1
    finally:
        app.dependency_overrides.clear()
        test_container.repository.close()
