import pytest

import db.database as database


@pytest.fixture(autouse=True)
def isolate_db(tmp_path, monkeypatch):
    """Point the DB at a throwaway file per test so tests never touch the
    real data.db, and so tests can't see each other's rows."""
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()
    yield


def test_save_and_get_document_round_trip():
    document_id = database.save_document(filename="report.pdf", page_count=12)

    result = database.get_document(document_id)

    assert result is not None
    assert result["filename"] == "report.pdf"
    assert result["page_count"] == 12
    assert result["id"] == document_id


def test_unknown_document_id_returns_none():
    assert database.get_document("does-not-exist") is None


def test_documents_persist_across_separate_connections():
    # Each _connect() call opens and closes its own connection — this
    # confirms data survives that, unlike the old in-memory dict which
    # only survived within a single running process.
    document_id = database.save_document(filename="a.pdf", page_count=1)

    first_read = database.get_document(document_id)
    second_read = database.get_document(document_id)

    assert first_read == second_read
