from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class StoredChunk:
    chunk_id: str
    document_id: str
    source_id: str
    title: str
    text: str
    position: int


class SQLiteRepository:
    def __init__(self, path: str) -> None:
        self.path = path
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._memory_connection: sqlite3.Connection | None = None
        if path == ":memory:":
            self._memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_connection.row_factory = sqlite3.Row
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        if self._memory_connection is not None:
            yield self._memory_connection
            return
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def close(self) -> None:
        if self._memory_connection is not None:
            self._memory_connection.close()
            self._memory_connection = None

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS audits (
                    id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL
                );
                """
            )
            connection.commit()

    def upsert_document(
        self,
        *,
        source_id: str,
        title: str,
        text: str,
        metadata: dict[str, Any],
        chunks: list[str],
    ) -> tuple[str, int]:
        document_id = str(uuid4())
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT id FROM documents WHERE source_id = ?", (source_id,)
            ).fetchone()
            if existing:
                document_id = str(existing["id"])
                connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
                connection.execute(
                    "UPDATE documents SET title = ?, text = ?, metadata_json = ? WHERE id = ?",
                    (title, text, json.dumps(metadata), document_id),
                )
            else:
                connection.execute(
                    (
                        "INSERT INTO documents(id, source_id, title, text, metadata_json) "
                        "VALUES(?, ?, ?, ?, ?)"
                    ),
                    (document_id, source_id, title, text, json.dumps(metadata)),
                )
            for position, chunk in enumerate(chunks):
                connection.execute(
                    "INSERT INTO chunks(id, document_id, position, text) VALUES(?, ?, ?, ?)",
                    (str(uuid4()), document_id, position, chunk),
                )
            connection.commit()
        return document_id, len(chunks)

    def list_chunks(self) -> list[StoredChunk]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT c.id AS chunk_id, c.document_id, c.position, c.text,
                       d.source_id, d.title
                FROM chunks c
                JOIN documents d ON d.id = c.document_id
                ORDER BY d.source_id, c.position
                """
            ).fetchall()
        return [
            StoredChunk(
                chunk_id=str(row["chunk_id"]),
                document_id=str(row["document_id"]),
                source_id=str(row["source_id"]),
                title=str(row["title"]),
                text=str(row["text"]),
                position=int(row["position"]),
            )
            for row in rows
        ]

    def save_audit(self, payload: dict[str, Any]) -> str:
        audit_id = str(uuid4())
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO audits(id, payload_json) VALUES(?, ?)",
                (audit_id, json.dumps(payload)),
            )
            connection.commit()
        return audit_id

    def get_audit(self, audit_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM audits WHERE id = ?", (audit_id,)
            ).fetchone()
        if row is None:
            return None
        return cast(dict[str, Any], json.loads(str(row["payload_json"])))
