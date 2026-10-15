import pytest

from evidence_rag.contracts import VersionInput
from evidence_rag.documents.chunking import chunk_document


def test_chunks_keep_unicode_offsets() -> None:
    text = "# Flow\nCaf\u00e9 display: 35 units.\n" + ("z" * 1200)
    chunks = chunk_document("v2", text)
    assert len(chunks) > 1
    assert all(text[c.start_char : c.end_char] == c.text for c in chunks)
    assert all(len(c.text) <= 1000 for c in chunks)
    assert len({c.id for c in chunks}) == len(chunks)


def test_admission_rejects_empty_html_and_large_input() -> None:
    for text in (" ", "<script>alert(1)</script>"):
        with pytest.raises(ValueError):
            VersionInput(title="A", label="v2", effective_date="2026-10-15", markdown=text)
    with pytest.raises(ValueError):
        VersionInput(title="A", label="v2", effective_date="yesterday", markdown="body")
