from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status

from veritrag.container import Container, get_container
from veritrag.models import AuditIn, AuditOut, DocumentIn, DocumentOut, SearchIn, SearchOut

app = FastAPI(
    title="VeriRAG",
    version="0.1.0",
    description="Evidence-first reliability gateway for retrieval-augmented generation systems.",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def ingest_document(
    document: DocumentIn,
    container: Container = Depends(get_container),
) -> DocumentOut:
    try:
        return container.indexing.ingest(document)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/search", response_model=SearchOut)
def search(
    request: SearchIn,
    container: Container = Depends(get_container),
) -> SearchOut:
    return container.search.search(request.query, request.top_k)


@app.post("/v1/audits", response_model=AuditOut)
def audit(
    request: AuditIn,
    container: Container = Depends(get_container),
) -> AuditOut:
    return container.audit.audit(request)


@app.get("/v1/audits/{audit_id}", response_model=AuditOut)
def get_audit(
    audit_id: str,
    container: Container = Depends(get_container),
) -> AuditOut:
    payload = container.repository.get_audit(audit_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Audit not found")
    return AuditOut(audit_id=audit_id, **payload)
