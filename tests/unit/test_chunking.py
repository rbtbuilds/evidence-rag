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


def test_repeated_and_suffixed_headings_have_unique_sections() -> None:
    text = "# Flow\nFirst.\n# Flow\nSecond.\n# Flow-2\nThird.\n# Flow\nFourth.\n# !!!\nFifth.\n# !!!\nSixth."
    chunks = chunk_document("version", text)
    assert len(chunks) == 6
    assert len({c.section_id for c in chunks}) == 6
    assert all(c.section_id for c in chunks)
