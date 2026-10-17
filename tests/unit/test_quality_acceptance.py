from evidence_rag.evaluation.quality_acceptance import acceptance_gates


def counts() -> tuple[dict[str, int], dict[str, int]]:
    regression = {
        "cases": 192,
        "expected_refusals": 48,
        "proper_refusals": 48,
        "answerable": 144,
        "answerable_responses": 120,
        "invalid_outputs": 0,
        "forbidden_disclosures": 0,
        "citations": 120,
        "resolved_citations": 120,
    }
    challenge = {
        "cases": 96,
        "expected_refusals": 32,
        "proper_refusals": 32,
        "answerable": 64,
        "answerable_responses": 56,
        "oracle_verified_complete": 56,
        "oracle_unverified_responses": 0,
        "invalid_outputs": 0,
        "forbidden_disclosures": 0,
        "citations": 56,
        "resolved_citations": 56,
    }
    return regression, challenge


def test_gate_requires_both_correct_refusals_and_useful_coverage() -> None:
    regression, challenge = counts()
    assert all(acceptance_gates(regression, challenge).values())
    regression.update(proper_refusals=46, answerable_responses=109)
    assert not acceptance_gates(regression, challenge)["regression_refusals"]
    assert not acceptance_gates(regression, challenge)["regression_coverage"]
    regression, challenge = counts()
    challenge["oracle_verified_complete"] = 40
    assert not acceptance_gates(regression, challenge)["challenge_useful_coverage"]
    challenge["oracle_unverified_responses"] = 1
    assert not acceptance_gates(regression, challenge)["challenge_no_unverified_answers"]


def test_empty_partial_or_unresolved_blocks_cannot_pass() -> None:
    regression, challenge = counts()
    challenge.update(cases=12, citations=0, resolved_citations=0)
    gates = acceptance_gates(regression, challenge)
    assert not gates["complete_blocks"] and not gates["citation_resolution"]
    regression, challenge = counts()
    challenge["resolved_citations"] = 55
    assert not acceptance_gates(regression, challenge)["citation_resolution"]
