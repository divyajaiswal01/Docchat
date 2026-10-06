"""
Thin wrapper around the Groq API (free tier, OpenAI-compatible).

Phase 2: instead of stuffing the whole document into the prompt (Phase 1),
we only send the chunks retrieval decided are actually relevant to the
question. This is what lets the app scale to long documents without
blowing past context limits or wasting tokens.

Phase 3 adds a streaming variant (stream_answer) so the UI can render
tokens as they arrive instead of waiting for the full response.
"""

import os
from typing import Iterator

from groq import Groq, APIError, APITimeoutError

_client: Groq | None = None


class LLMError(Exception):
    pass


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise LLMError("GROQ_API_KEY is not set. Check your .env file.")
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = (
    "You answer questions using ONLY the excerpts provided below, which come "
    "from a larger document. If the answer isn't contained in these excerpts, "
    "say so clearly instead of guessing. Be concise and direct."
)

# Confirmed available on Groq's free tier for this account via
# `curl .../v1/models` (see README). Large 131k context window, supports
# tool calling and structured outputs if needed later.
MODEL_NAME = "openai/gpt-oss-20b"


def _format_chunks(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        page = chunk.get("page")
        label = f"[Page {page}]" if page is not None else "[Excerpt]"
        parts.append(f"{label}\n{chunk['text']}")
    return "\n\n---\n\n".join(parts)


def answer_question(chunks: list[dict], question: str) -> str:
    """
    chunks: the retrieved chunks from vector_store.query_chunks, each
    {"text": ..., "page": ...}. These replace the "stuff the whole doc in"
    approach from Phase 1.
    """
    if not chunks:
        return (
            "I couldn't find anything relevant to that question in the "
            "document. Try rephrasing, or ask about something else in the text."
        )

    client = _get_client()

    user_content = (
        f"DOCUMENT EXCERPTS:\n{_format_chunks(chunks)}\n\n"
        f"QUESTION:\n{question}"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
        )
    except APITimeoutError as exc:
        raise LLMError("The request to Groq timed out. Try again.") from exc
    except APIError as exc:
        raise LLMError(f"Groq API error: {exc}") from exc

    choice = response.choices[0] if response.choices else None
    if choice is None or not choice.message or not choice.message.content:
        raise LLMError("Groq returned an empty response.")

    return choice.message.content


def stream_answer(chunks: list[dict], question: str) -> Iterator[str]:
    """
    Same inputs/behavior as answer_question, but yields text deltas as they
    arrive from Groq instead of returning the full string at once.
    """
    if not chunks:
        yield (
            "I couldn't find anything relevant to that question in the "
            "document. Try rephrasing, or ask about something else in the text."
        )
        return

    client = _get_client()

    user_content = (
        f"DOCUMENT EXCERPTS:\n{_format_chunks(chunks)}\n\n"
        f"QUESTION:\n{question}"
    )

    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            stream=True,
        )
        for event in stream:
            if not event.choices:
                continue
            delta = event.choices[0].delta.content
            if delta:
                yield delta
    except APITimeoutError as exc:
        raise LLMError("The request to Groq timed out. Try again.") from exc
    except APIError as exc:
        raise LLMError(f"Groq API error: {exc}") from exc
