from evidence_rag.contracts import Answer
from evidence_rag.evaluation.report import EvaluationRow
from evidence_rag.evaluation.run import aggregate


def row(expected: bool, reason: str | None) -> EvaluationRow:
    return EvaluationRow(
        query_id="diagnostic",
        question="Which fact is stated?",
        role="reader",
        stratum="unsupported" if expected else "supported",
        mode="bm25",
        relevant_sections=[] if expected else ["fact"],
        retrieved_sections=[],
        expected_facts=[],
        expected_abstention=expected,
        answer=Answer(
            request_id="diagnostic",
            execution_profile="local",
            retrieval_mode="bm25",
            generation_mode="local",
            answer="A fact" if reason is None else "",
            abstained=reason is not None,
            reason=reason,
            citations=[],
            timings_ms={},
        ),
        recall_at_5=None if expected else 0,
        mrr_at_5=0,
        forbidden_disclosure=False,
        citations_valid=0,
        latency_ms=1,
        embedding_truncations=0,
        dropped_passages=0,
    )


def test_format_rejection_is_not_an_explicit_correct_refusal() -> None:
    measured = aggregate(
        [
            row(True, "insufficient_evidence"),
            row(True, "invalid_generation"),
            row(True, None),
            row(False, None),
            row(False, "insufficient_evidence"),
        ]
    ).model_dump()
    assert measured["correct_abstentions"] == 2
    assert measured.get("explicit_correct_abstentions") == 1
    assert measured.get("invalid_generation_count") == 1
    assert measured.get("answerable_count") == 2
    assert measured.get("answered_answerable_count") == 1
    assert measured.get("unnecessary_abstentions") == 1


def test_refusing_everything_exposes_lost_answerable_responses() -> None:
    measured = aggregate(
        [row(True, "insufficient_evidence"), row(False, "insufficient_evidence")]
    ).model_dump()
    assert measured.get("explicit_correct_abstentions") == 1
    assert measured.get("answered_answerable_count") == 0
    assert measured.get("unnecessary_abstentions") == 1
