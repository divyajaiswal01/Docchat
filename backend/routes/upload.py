from fastapi import APIRouter, File, HTTPException, UploadFile

from models.schema import UploadResponse
from services.chunker import chunk_pages
from services.pdf_parser import PDFParseError, extract_pages
from services.vector_store import store_chunks
from store import save_document_metadata

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        pages_text = await extract_pages(file)
    except PDFParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks = chunk_pages(pages_text)
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Couldn't extract any usable text chunks from this PDF.",
        )

    filename = file.filename or "untitled.pdf"
    document_id = save_document_metadata(filename=filename, page_count=len(pages_text))

    # Embeds + persists all chunks in Chroma under this document_id.
    store_chunks(document_id, chunks)

    return UploadResponse(
        document_id=document_id,
        filename=filename,
        page_count=len(pages_text),
        char_count=sum(len(p) for p in pages_text),
    )
