from uuid import uuid4

from evidence_rag.contracts import RetrievalMode, VersionInput
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.documents.ingest import seed
from evidence_rag.models.fixture import FixtureEmbedder, FixtureReranker
from evidence_rag.retrieval.service import Retriever, build_index
from tests.helpers import DemoHarness

MODES: tuple[RetrievalMode, ...] = ("bm25", "dense", "hybrid", "hybrid_rerank")


def test_access_before_scoring_and_reader_rank_invariance(demo: DemoHarness) -> None:
    seed(demo.repo)
    reader = demo.repo.resolve_scope(demo.reader()["Cookie"].split("=", 1)[1])
    maintainer = demo.repo.resolve_scope(demo.maintainer()["Cookie"].split("=", 1)[1])
    retriever = Retriever(demo.repo, FixtureEmbedder(), FixtureReranker())
    for mode in MODES:
        privileged = retriever.retrieve(maintainer, "calibration marker", mode)
        assert any("MAINTAINER-CAL-7391" in c.text for c in privileged)
        result = retriever.retrieve(reader, "calibration marker", mode)
        assert all("MAINTAINER-CAL-7391" not in c.text for c in result)
        assert len(result) <= 5
    before = retriever.retrieve(reader, "circulation display limit", "bm25")
    text = "# Private\nCirculation display limit hidden secret."
    draft = build_index(chunk_document(str(uuid4()), text), FixtureEmbedder())
    demo.repo.publish(
        str(uuid4()),
        0,
        draft,
        VersionInput(
            title="Private",
            label="v1",
            min_role="maintainer",
            effective_date="2026-10-15",
            markdown=text,
        ),
    )
    assert before == retriever.retrieve(reader, "circulation display limit", "bm25")
    for mode in MODES:
        assert retriever.retrieve(reader, "???", mode) == []
        assert len(retriever.retrieve(reader, '" OR NEAR ( display', mode)) <= 5
