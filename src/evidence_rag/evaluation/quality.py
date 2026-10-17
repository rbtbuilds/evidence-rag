"""Frozen, narrow source-grounded oracles; never part of inference policy."""

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from evidence_rag.contracts import Answer, Role, StrictModel
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.documents.ingest import FIXTURES, contained, validate_corpus
from evidence_rag.models.local import PROJECT

QUALITY_ROOT = FIXTURES / "quality-v1"


class QualityCase(StrictModel):
    id: str
    question: str = Field(min_length=1, max_length=500)
    role: Role
    category: str
    expected_abstention: bool
    expected_facts: list[str]
    support_sections: list[str]
    support_quotes: list[str]
    forbidden_strings: list[str]
    rationale: str
    reference_answer: str = Field(max_length=180)
    accepted_claims: list[str]


class FrozenManifest(BaseModel):
    files: dict[str, str]
    source_hashes: dict[str, str]
    acceptance: dict[str, str | int | float | bool] = {}


@dataclass(frozen=True)
class QualityScore:
    proper_refusal: bool
    claim_form_matches: bool
    cited_support_matches: bool
    oracle_verified: bool


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def claim_matches(case: QualityCase, text: str) -> bool:
    return any(
        re.fullmatch(pattern, text.strip(), re.IGNORECASE) for pattern in case.accepted_claims
    )


def load_cases(
    split: Literal["dev", "challenge"], *, root: Path = QUALITY_ROOT, verify_sources: bool = True
) -> list[QualityCase]:
    anchor = root / "manifest.sha256"
    if anchor.exists():
        if anchor.read_text().strip().split() != [sha256(root / "manifest.json"), "manifest.json"]:
            raise ValueError("Frozen manifest hash mismatch")
    elif verify_sources:
        raise ValueError("Missing frozen manifest hash anchor")
    manifest = FrozenManifest.model_validate_json((root / "manifest.json").read_text())
    name = f"{split}.json"
    path = contained(root, name)
    if manifest.files.get(name) != sha256(path):
        raise ValueError("Frozen case hash mismatch")
    if verify_sources:
        criteria = manifest.acceptance
        criteria_path = contained(PROJECT, str(criteria.get("criteria_document", "")))
        if sha256(criteria_path) != criteria.get("criteria_document_sha256"):
            raise ValueError("Frozen criteria hash mismatch")
        for relative, digest in manifest.files.items():
            if sha256(contained(root, relative)) != digest:
                raise ValueError("Frozen case hash mismatch")
        for relative, digest in manifest.source_hashes.items():
            if sha256(contained(FIXTURES, relative)) != digest:
                raise ValueError("Frozen source hash mismatch")
    cases = [QualityCase.model_validate(item) for item in json.loads(path.read_text())]
    if not cases or len({case.id for case in cases}) != len(cases):
        raise ValueError("Empty or duplicate cases")
    corpus = validate_corpus() if verify_sources else None
    for case in cases:
        if case.expected_abstention:
            if any(
                (
                    case.reference_answer,
                    case.accepted_claims,
                    case.expected_facts,
                    case.support_quotes,
                    case.support_sections,
                )
            ):
                raise ValueError("Refusal oracle contains an answer")
        elif not (
            case.support_quotes
            and case.support_sections
            and case.expected_facts
            and case.reference_answer
            and claim_matches(case, case.reference_answer)
        ):
            raise ValueError("Incomplete or inconsistent reference answer oracle")
        if corpus and not case.expected_abstention:
            passages = [
                chunk.text
                for record in corpus.documents
                if record.status == "active"
                and (case.role == "maintainer" or record.min_role == "reader")
                for chunk in chunk_document(
                    record.version_id, (FIXTURES / "corpus" / record.path).read_text()
                )
                if chunk.section_id in case.support_sections
            ]
            if not all(
                any(quote in passage for passage in passages) for quote in case.support_quotes
            ):
                raise ValueError("Reference support is absent from accessible current source")
    return cases


def score_answer(case: QualityCase, answer: Answer, *, citations_valid: bool) -> QualityScore:
    proper = (
        case.expected_abstention
        and answer.abstained
        and answer.reason == "insufficient_evidence"
        and not answer.answer
        and not answer.citations
    )
    disclosure = any(
        value.casefold() in answer.model_dump_json().casefold() for value in case.forbidden_strings
    )
    form = (
        not case.expected_abstention
        and not answer.abstained
        and answer.reason is None
        and not disclosure
        and claim_matches(case, answer.answer)
    )
    support = (
        not case.expected_abstention
        and not answer.abstained
        and citations_valid
        and bool(answer.citations)
        and all(c.section_id in case.support_sections for c in answer.citations)
        and all(any(quote in c.quote for c in answer.citations) for quote in case.support_quotes)
    )
    return QualityScore(proper, form, support, form and support)
