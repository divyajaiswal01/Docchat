from services.chunker import chunk_pages
from config import CHUNK_SIZE_CHARS


def test_empty_pages_produce_no_chunks():
    assert chunk_pages(["", "   ", ""]) == []


def test_short_page_produces_one_chunk():
    pages = ["This is a short page of text."]
    chunks = chunk_pages(pages)

    assert len(chunks) == 1
    assert chunks[0].page == 1
    assert chunks[0].text == pages[0]


def test_long_page_splits_into_overlapping_chunks():
    # Build a page clearly longer than one chunk so it must split.
    long_text = "word " * (CHUNK_SIZE_CHARS // 4)  # ~2x chunk size
    chunks = chunk_pages([long_text])

    assert len(chunks) > 1
    # All chunks should be tagged with page 1.
    assert all(c.page == 1 for c in chunks)
    # Consecutive chunks should overlap: the tail of one chunk reappears
    # at the start of the next, which is the whole point of overlap — it
    # stops an answer that spans a chunk boundary from getting cut in half.
    first_tail = chunks[0].text[-50:]
    assert first_tail in chunks[1].text
    assert chunks[0].text != chunks[1].text


def test_chunk_ids_are_unique_and_track_page_and_index():
    pages = ["short page one", "short page two"]
    chunks = chunk_pages(pages)

    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids)), "chunk ids must be unique"
    assert chunks[0].id == "page1-chunk0"
    assert chunks[1].id == "page2-chunk0"


def test_blank_pages_between_content_are_skipped_but_numbering_preserved():
    pages = ["page one content", "", "page three content"]
    chunks = chunk_pages(pages)

    pages_seen = {c.page for c in chunks}
    assert pages_seen == {1, 3}
    assert 2 not in pages_seen
