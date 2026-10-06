import pytest

import services.usage_limiter as usage_limiter


@pytest.fixture(autouse=True)
def isolate_counts(monkeypatch):
    """Each test starts with a clean counter dict and a small limit so
    tests don't need to fire 20 requests to prove the cap works."""
    monkeypatch.setattr(usage_limiter, "_counts", {})
    monkeypatch.setattr(usage_limiter, "MAX_QUESTIONS_PER_DOCUMENT", 3)
    yield


def test_remaining_count_decreases_with_each_question():
    assert usage_limiter.check_and_increment("doc-1") == 2
    assert usage_limiter.check_and_increment("doc-1") == 1
    assert usage_limiter.check_and_increment("doc-1") == 0


def test_exceeding_the_limit_raises():
    usage_limiter.check_and_increment("doc-1")
    usage_limiter.check_and_increment("doc-1")
    usage_limiter.check_and_increment("doc-1")  # uses up the 3rd and last

    with pytest.raises(usage_limiter.UsageLimitExceeded):
        usage_limiter.check_and_increment("doc-1")


def test_documents_have_independent_counters():
    usage_limiter.check_and_increment("doc-1")
    usage_limiter.check_and_increment("doc-1")

    # doc-2 should be unaffected by doc-1's usage.
    assert usage_limiter.check_and_increment("doc-2") == 2
