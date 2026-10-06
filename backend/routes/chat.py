import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from config import TOP_K_CHUNKS
from models.schema import ChatRequest
from services.llm import LLMError, stream_answer
from services.usage_limiter import UsageLimitExceeded, check_and_increment
from services.vector_store import query_chunks
from store import get_document_metadata

router = APIRouter()


def _sse(event: dict) -> str:
    """Formats a dict as one Server-Sent Events message."""
    return f"data: {json.dumps(event)}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    document = get_document_metadata(request.document_id)
    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Upload it again — the server may have restarted.",
        )

    try:
        remaining_questions = check_and_increment(request.document_id)
    except UsageLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    relevant_chunks = query_chunks(
        document_id=request.document_id,
        question=request.question,
        top_k=TOP_K_CHUNKS,
    )

    def event_generator():
        try:
            for delta in stream_answer(relevant_chunks, request.question):
                yield _sse({"type": "token", "content": delta})
        except LLMError as exc:
            yield _sse({"type": "error", "message": str(exc)})
            return

        # Citations: which pages the answer was actually grounded in.
        pages = sorted({c["page"] for c in relevant_chunks if c.get("page") is not None})
        yield _sse({"type": "sources", "pages": pages})
        yield _sse({"type": "done", "remaining_questions": remaining_questions})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
