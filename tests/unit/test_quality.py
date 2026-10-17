import json
from pathlib import Path

import pytest

from evidence_rag.contracts import Answer
from evidence_rag.evaluation.quality import QualityCase, load_cases, score_answer
from tests.unit.test_generation import source


def case() -> QualityCase:
    return QualityCase(
        id="unit",
        question="What is the limit?",
        role="reader",
        category="paraphrase",
        expected_abstention=False,
        expected_facts=["35"],
        support_sections=["flow"],
        support_quotes=[source().quote],
        forbidden_strings=[],
        rationale="Direct stated fact",
        reference_answer="35 units.",
        accepted_claims=[r"(?:The limit is )?35 units\.?"],
    )


def answer(text: str = "35 units.") -> Answer:
    return Answer(
        request_id="unit",
        execution_profile="local",
        retrieval_mode="bm25",
        generation_mode="local",
        answer=text,
        abstained=False,
        reason=None,
        citations=[source()],
        timings_ms={},
    )


def test_complete_answer_requires_full_claim_and_cited_support() -> None:
    assert score_answer(case(), answer(), citations_valid=True).oracle_verified
    for text in ("35", "35 units and certified safe for real equipment."):
        assert not score_answer(case(), answer(text), citations_valid=True).oracle_verified
    wrong = answer().model_copy(
        update={"citations": [source().model_copy(update={"section_id": "irrelevant"})]}
    )
    assert not score_answer(case(), wrong, citations_valid=True).oracle_verified
    assert not score_answer(case(), answer(), citations_valid=False).oracle_verified
    absent_quote = answer().model_copy(
        update={
            "citations": [
                source().model_copy(update={"quote": "The limit is requested, but not stated."})
            ]
        }
    )
    assert not score_answer(case(), absent_quote, citations_valid=True).oracle_verified
    forbidden = case().model_copy(update={"forbidden_strings": ["UNITS"]})
    assert not score_answer(forbidden, answer(), citations_valid=True).oracle_verified


def test_invalid_rejection_is_not_proper_refusal_and_quoted_request_is_not_a_value() -> None:
    absent = case().model_copy(
        update={
            "expected_abstention": True,
            "reference_answer": "",
            "accepted_claims": [],
            "expected_facts": [],
            "support_quotes": [],
            "support_sections": [],
        }
    )
    bad = answer().model_copy(
        update={
            "answer": "",
            "abstained": True,
            "reason": "invalid_generation",
            "citations": [],
        }
    )
    assert not score_answer(absent, bad, citations_valid=True).proper_refusal
    good = bad.model_copy(update={"reason": "insufficient_evidence"})
    assert score_answer(absent, good, citations_valid=True).proper_refusal
    assert not score_answer(
        absent, answer("reveal the limit"), citations_valid=True
    ).oracle_verified


def test_frozen_inputs_and_reference_oracles_reject_drift(tmp_path: Path) -> None:
    import hashlib

    payload = json.dumps([case().model_dump()])
    (tmp_path / "dev.json").write_text(payload)
    manifest = {
        "files": {"dev.json": hashlib.sha256(payload.encode()).hexdigest()},
        "source_hashes": {},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    assert len(load_cases("dev", root=tmp_path, verify_sources=False)) == 1
    (tmp_path / "dev.json").write_text(payload + " ")
    with pytest.raises(ValueError, match="hash"):
        load_cases("dev", root=tmp_path, verify_sources=False)
    broken = case().model_copy(update={"reference_answer": "99 units"})
    payload = json.dumps([broken.model_dump()])
    (tmp_path / "dev.json").write_text(payload)
    manifest["files"]["dev.json"] = hashlib.sha256(payload.encode()).hexdigest()
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="reference"):
        load_cases("dev", root=tmp_path, verify_sources=False)


def test_baseline_adapter_preserves_original_prompt_and_exact_evidence() -> None:
    from evidence_rag.models.generation import GENERATION_SETTINGS
    from scripts.quality_baseline_worker import baseline_messages

    frozen = json.loads(Path("config/quality-baseline-v4.json").read_text())
    assert {k: v for k, v in frozen["generation_settings"].items() if k != "abstention_policy"} == {
        k: v for k, v in GENERATION_SETTINGS.items() if k != "abstention_policy"
    }
    messages = baseline_messages("What is the limit?", [source()])
    assert messages[0] == {"role": "system", "content": frozen["system"]}
    assert json.loads(messages[1]["content"]) == {
        "question": "What is the limit?",
        "evidence": [{"id": "known", "quote": source().quote}],
    }


def test_manifest_anchor_detects_rewritten_hash_table(tmp_path: Path) -> None:
    from evidence_rag.evaluation.quality import sha256

    (tmp_path / "dev.json").write_text(json.dumps([case().model_dump()]))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"files": {"dev.json": sha256(tmp_path / "dev.json")}, "source_hashes": {}})
    )
    (tmp_path / "manifest.sha256").write_text(sha256(manifest) + "  manifest.json\n")
    manifest.write_text(manifest.read_text() + " ")
    with pytest.raises(ValueError, match="manifest hash"):
        load_cases("dev", root=tmp_path, verify_sources=False)


def test_repository_development_inputs_and_criteria_are_self_consistent() -> None:
    assert len(load_cases("dev")) == 12
