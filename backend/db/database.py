"""
SQLite storage for document metadata (filename, page count).

This replaces the in-memory dict used in Phase 1-3. That dict reset every
time the backend restarted, which meant previously-uploaded documents
became unreachable (their chunks were still in Chroma on disk, but nothing
knew their filename/page count anymore). SQLite is a single file, needs no
server, and survives restarts — the simplest fix that actually solves it.
"""

import os
import sqlite3
import uuid
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                page_count INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_document(filename: str, page_count: int) -> str:
    document_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, page_count) VALUES (?, ?, ?)",
            (document_id, filename, page_count),
        )
    return document_id


def get_document(document_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, filename, page_count FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return dict(row) if row else None
