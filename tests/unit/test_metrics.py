from evidence_rag.evaluation.metrics import mrr_at_k, paired_interval, recall_at_k


def test_repeated_section_is_not_extra_relevance() -> None:
    assert recall_at_k(["a", "a", "b"], {"a", "c"}, 5) == 0.5
    assert mrr_at_k(["x", "a", "a"], {"a"}, 5) == 0.5
    assert mrr_at_k(["x"], {"a"}, 5) == 0
    assert recall_at_k(["a"], set(), 5) is None


def test_bootstrap_fixed_seed_and_known_difference() -> None:
    assert paired_interval([0.5] * 8) == (0.5, 0.5)
    assert paired_interval([0, 1, -1, 0.5]) == paired_interval([0, 1, -1, 0.5])
