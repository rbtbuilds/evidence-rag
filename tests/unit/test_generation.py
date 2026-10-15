from evidence_rag.answers.generation import extractive, validate_generation
from evidence_rag.contracts import Citation


def source() -> Citation:
    return Citation(
        chunk_id="known",
        document_id="d",
        version_id="v",
        title="Flow",
        version_label="v2",
        effective_date="2026-10-15",
        section_id="flow",
        start_char=0,
        end_char=43,
        quote="The circulation display limit is 35 units.",
    )


def test_unknown_citations_and_malformed_schema_abstain() -> None:
    for text in [
        '{"answer":"35","cited_chunk_ids":["unknown"],"insufficient_evidence":false}',
        '{"answer":"35","citation_ids":["known"]}',
        "not json",
    ]:
        result = validate_generation(text, [source()])
        assert result.abstained and result.reason == "invalid_generation" and not result.citations
    result = validate_generation(
        '{"answer":"35","cited_chunk_ids":["known"],"insufficient_evidence":false}', [source()]
    )
    assert not result.abstained and result.citations[0].chunk_id == "known"


def test_extractive_quotes_and_abstention() -> None:
    result = extractive("What is the circulation display limit?", [source()])
    assert "35 units." in result.text and not result.abstained
    assert extractive("Certified orbital pressure?", [source()]).abstained
