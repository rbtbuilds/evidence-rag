import hashlib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from evidence_rag.contracts import Role, VersionInput
from evidence_rag.db.repository import Repository
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.models.fixture import FixtureEmbedder
from evidence_rag.retrieval.service import build_index

FIXTURES = Path(__file__).resolve().parents[3] / "fixtures"


class SourceRecord(BaseModel):
    logical_id: str
    document_id: str
    version_id: str
    path: str
    title: str
    label: str
    effective_date: str
    min_role: Role
    status: Literal["active", "superseded"]
    sha256: str
    sections: list[str]


class Tombstone(BaseModel):
    logical_id: str
    document_id: str
    deleted: bool


class CorpusManifest(BaseModel):
    revision: str
    owner: str
    license: str
    provenance: str
    documents: list[SourceRecord]
    tombstones: list[Tombstone]


class Question(BaseModel):
    id: str
    question: str
    stratum: Literal["supported", "unsupported", "version-conflict", "restricted"]
    role: Role
    relevant_sections: list[str]
    expected_facts: list[str]
    expected_abstention: bool
    forbidden_strings: list[str]
    template: str
    section_family: str


class SplitManifest(BaseModel):
    revision: str
    development_count: int
    test_count: int
    grouping: str
    hashes: dict[str, str]


def contained(root: Path, relative: str) -> Path:
    path = Path(relative)
    resolved = (root / path).resolve()
    if path.is_absolute() or not resolved.is_relative_to(root.resolve()):
        raise ValueError("Fixture path escapes root")
    return resolved


def validate_corpus(root: Path = FIXTURES) -> CorpusManifest:
    manifest = CorpusManifest.model_validate_json((root / "corpus/manifest.json").read_text())
    if len(manifest.documents) != 24 or len({d.document_id for d in manifest.documents}) != 12:
        raise ValueError("Expected 12 two-version documents")
    for record in manifest.documents:
        source = contained(root / "corpus", record.path).read_text()
        if hashlib.sha256(source.encode()).hexdigest() != record.sha256:
            raise ValueError("Source hash mismatch")
        chunks = chunk_document(record.version_id, source)
        if {c.section_id for c in chunks} != set(record.sections):
            raise ValueError("Section mismatch")
        for section in record.sections:
            group = [c for c in chunks if c.section_id == section]
            text = source[min(c.start_char for c in group) : max(c.end_char for c in group)]
            if not 80 <= len(text.split()) <= 160:
                raise ValueError(f"Section word budget: {section}")
    split = SplitManifest.model_validate_json((root / "questions/split.json").read_text())
    for relative, digest in split.hashes.items():
        if hashlib.sha256(contained(root, relative).read_bytes()).hexdigest() != digest:
            raise ValueError("Frozen split hash mismatch")
    for name, size, counts in [("dev", 24, [12, 4, 4, 4]), ("test", 48, [24, 8, 8, 8])]:
        items = load_questions(name, root)
        if len(items) != size or len({q.id for q in items}) != size:
            raise ValueError("Question count mismatch")
        if [
            sum(q.stratum == s for q in items)
            for s in ("supported", "unsupported", "version-conflict", "restricted")
        ] != counts:
            raise ValueError("Stratum count mismatch")
    dev = load_questions("dev", root)
    test = load_questions("test", root)
    if {q.template for q in dev} & {q.template for q in test} or {q.section_family for q in dev} & {
        q.section_family for q in test
    }:
        raise ValueError("Split group leakage")
    return manifest


def load_questions(split: str, root: Path = FIXTURES) -> list[Question]:
    if split not in {"dev", "test"}:
        raise ValueError("Unknown split")
    return [
        Question.model_validate_json(line)
        for line in (root / f"questions/{split}.jsonl").read_text().splitlines()
        if line.strip()
    ]


def seed(repo: Repository) -> None:
    manifest = validate_corpus()
    with repo.transaction() as db:
        if db.execute("SELECT 1 FROM documents LIMIT 1").fetchone():
            raise ValueError("Seeding requires an empty corpus")
        for record in manifest.documents:
            text = contained(FIXTURES / "corpus", record.path).read_text()
            chunks = chunk_document(record.version_id, text)
            metadata = VersionInput(
                title=record.title,
                min_role=record.min_role,
                label=record.label,
                effective_date=record.effective_date,
                markdown=text,
            )
            repo.publish_in_transaction(
                db,
                record.document_id,
                0 if record.label == "v1" else 1,
                build_index(chunks, FixtureEmbedder()),
                metadata,
            )
        for tombstone in manifest.tombstones:
            db.execute(
                "INSERT INTO documents VALUES(?, 'Deleted calibration bulletin','maintainer',NULL,'2026-03-01T00:00:00+00:00',1)",
                (tombstone.document_id,),
            )
