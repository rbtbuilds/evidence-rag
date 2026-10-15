from collections.abc import Sequence

import numpy as np


def recall_at_k(retrieved_sections: Sequence[str], relevant: set[str], k: int) -> float | None:
    if not relevant:
        return None
    ranked = list(dict.fromkeys(retrieved_sections))[:k]
    return len(set(ranked) & relevant) / len(relevant)


def mrr_at_k(retrieved_sections: Sequence[str], relevant: set[str], k: int) -> float:
    ranked = list(dict.fromkeys(retrieved_sections))[:k]
    first = next((i for i, section in enumerate(ranked, 1) if section in relevant), None)
    return 0.0 if first is None else 1 / first


def paired_interval(differences: Sequence[float]) -> tuple[float, float]:
    if not differences:
        return (0, 0)
    rng = np.random.default_rng(17)
    values = np.asarray(differences, dtype=np.float64)
    means = values[rng.integers(0, len(values), size=(2000, len(values)))].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))
