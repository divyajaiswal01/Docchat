"""
Thin wrapper around db.database so existing route imports
(`from store import save_document_metadata, get_document_metadata`) don't
need to change. The real persistence logic lives in db/database.py.
"""

from db.database import get_document, save_document


def save_document_metadata(filename: str, page_count: int) -> str:
    return save_document(filename, page_count)


def get_document_metadata(document_id: str) -> dict | None:
    return get_document(document_id)
