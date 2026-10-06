"""
Caps how many questions can be asked about a single uploaded document.

Why this exists: an unbounded loop of questions (a bug in the frontend, a
script someone points at your API, or just an enthusiastic user) burns
through your free Groq rate limit fast. This is a simple, honest guard —
not abuse-proof security, just a sane default.

In-memory by design: counts don't need to survive a restart (a fresh
restart is a reasonable place for a fresh budget), unlike document
metadata in Phase 4, which genuinely needed to persist.
"""

from config import MAX_QUESTIONS_PER_DOCUMENT

_counts: dict[str, int] = {}


class UsageLimitExceeded(Exception):
    pass


def check_and_increment(document_id: str) -> int:
    """
    Increments the question count for this document and returns how many
    questions remain. Raises UsageLimitExceeded if the cap is already hit.
    """
    current = _counts.get(document_id, 0)
    if current >= MAX_QUESTIONS_PER_DOCUMENT:
        raise UsageLimitExceeded(
            f"This document has reached its limit of {MAX_QUESTIONS_PER_DOCUMENT} "
            "questions. Upload it again to reset the limit."
        )

    _counts[document_id] = current + 1
    return MAX_QUESTIONS_PER_DOCUMENT - _counts[document_id]
