"""Pre-registered v1 gates; response presence is not complete supported answering."""

from evidence_rag.evaluation.quality import QUALITY_ROOT, FrozenManifest


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def acceptance_gates(regression: dict[str, int], challenge: dict[str, int]) -> dict[str, bool]:
    criteria = FrozenManifest.model_validate_json(
        (QUALITY_ROOT / "manifest.json").read_text()
    ).acceptance
    refusal = rate(challenge.get("proper_refusals", 0), challenge.get("expected_refusals", 0))
    useful = rate(challenge.get("oracle_verified_complete", 0), challenge.get("answerable", 0))
    return {
        "complete_blocks": regression.get("cases") == 192
        and challenge.get("cases") == 96
        and regression.get("expected_refusals") == 48
        and regression.get("answerable") == 144
        and challenge.get("expected_refusals") == 32
        and challenge.get("answerable") == 64,
        "regression_refusals": regression.get("proper_refusals", 0)
        >= int(criteria["existing_minimum_explicit_correct_refusals"]),
        "regression_coverage": regression.get("answerable_responses", 0)
        >= int(criteria["existing_minimum_nonrefused_answerable_rows"]),
        "challenge_refusals": refusal is not None
        and refusal >= float(criteria["challenge_minimum_explicit_refusal_correctness"]),
        "challenge_useful_coverage": useful is not None
        and useful
        >= float(criteria["challenge_minimum_oracle_verified_supported_complete_answer_coverage"]),
        "challenge_no_unverified_answers": challenge.get("oracle_unverified_responses") == 0,
        "no_invalid_or_disclosed_outputs": all(
            c.get("invalid_outputs") == 0 and c.get("forbidden_disclosures") == 0
            for c in (regression, challenge)
        ),
        "citation_resolution": all(
            c.get("citations", 0) > 0 and c.get("citations") == c.get("resolved_citations")
            for c in (regression, challenge)
        ),
    }
