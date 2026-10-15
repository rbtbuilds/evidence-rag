import math

from evidence_rag.models.fixture import FixtureEmbedder
from evidence_rag.retrieval.fusion import rrf
from evidence_rag.retrieval.types import Candidate


def test_rrf_rewards_agreement_without_duplicate_votes() -> None:
    a = Candidate("a", "flow", "flow", 1)
    b = Candidate("b", "limit", "limit", 0.9)
    c = Candidate("c", "pump", "pump", 0.8)
    result = rrf([[a, b, b], [c, b]])
    assert result[0].chunk_id == "b"
    assert abs(result[0].score - 2 / 62) < 1e-9


def test_embeddings_are_stable_normalized_and_defined_for_empty() -> None:
    model = FixtureEmbedder()
    vectors = model.embed(["Café display", "Café display", ""])
    assert vectors[0] == vectors[1]
    assert all(
        len(v) == 384 and math.isclose(sum(x * x for x in v), 1, abs_tol=1e-5) for v in vectors
    )


def test_oversized_query_and_corrupt_vectors_are_rejected() -> None:
    import pytest

    from evidence_rag.contracts import QuestionRequest

    with pytest.raises(ValueError):
        QuestionRequest(question="x" * 501)


def test_empty_reranking_does_not_call_a_model() -> None:
    from evidence_rag.retrieval.rerank import rerank

    class NoModel:
        revision = "test-no-call"

        def rerank(self, question: str, passages: list[str]) -> list[float]:
            raise AssertionError("No candidates must abstain without inference")

    assert rerank("empty", [], NoModel()) == []
