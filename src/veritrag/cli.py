from __future__ import annotations

import json
from pathlib import Path

import typer

from veritrag.container import get_container
from veritrag.models import AuditIn, DocumentIn

app = typer.Typer(help="VeriRAG: audit RAG/LLM answers against retrieved evidence.")


@app.command()
def ingest(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    source_id: str = typer.Option(
        ..., help="Stable source identifier used for idempotent updates."
    ),
    title: str = typer.Option(..., help="Human-readable document title."),
) -> None:
    text = path.read_text(encoding="utf-8")
    result = get_container().indexing.ingest(
        DocumentIn(source_id=source_id, title=title, text=text)
    )
    typer.echo(json.dumps(result.model_dump(), indent=2))


@app.command()
def search(query: str, top_k: int = typer.Option(5, min=1, max=20)) -> None:
    result = get_container().search.search(query, top_k)
    typer.echo(json.dumps(result.model_dump(), indent=2))


@app.command()
def audit(
    question: str = typer.Option(...),
    answer: str = typer.Option(...),
    top_k: int = typer.Option(6, min=1, max=20),
    fail_on_risk: bool = typer.Option(
        False,
        "--fail-on-risk",
        help="Exit non-zero when the audit fails, enabling CI quality gates.",
    ),
) -> None:
    result = get_container().audit.audit(
        AuditIn(question=question, answer=answer, top_k=top_k)
    )
    typer.echo(json.dumps(result.model_dump(), indent=2))
    if fail_on_risk and not result.passed:
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
