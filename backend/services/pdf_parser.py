"""
PDF text extraction.

Returns text PER PAGE (not one joined blob) so later stages can tag each
chunk with the page it came from — needed for Phase 3 citations, and
useful right now for more precise retrieval.
"""

import io

import pdfplumber
from fastapi import UploadFile

from config import MAX_FILE_SIZE_BYTES


class PDFParseError(Exception):
    pass


async def extract_pages(file: UploadFile) -> list[str]:
    """
    Returns a list of page texts, index 0 = page 1, etc.
    Raises PDFParseError on anything that would otherwise crash the request.
    """
    if file.content_type != "application/pdf":
        raise PDFParseError("Only PDF files are supported right now.")

    raw_bytes = await file.read()

    if len(raw_bytes) == 0:
        raise PDFParseError("The uploaded file is empty.")

    if len(raw_bytes) > MAX_FILE_SIZE_BYTES:
        raise PDFParseError("File is too large. Max size is 10MB.")

    try:
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:
        raise PDFParseError(f"Could not read this PDF: {exc}") from exc

    if not any(text.strip() for text in pages_text):
        raise PDFParseError(
            "No extractable text found. This may be a scanned/image-only PDF "
            "(OCR support isn't available yet)."
        )

    return pages_text
