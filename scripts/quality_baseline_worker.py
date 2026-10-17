"""Benchmark-only replay of the unchanged v4 prompt, with the same decoder."""

import json

from evidence_rag.contracts import Citation
from evidence_rag.models import worker
from evidence_rag.models.local import PROJECT


def baseline_messages(question: str, citations: list[Citation]) -> list[dict[str, str]]:
    frozen = json.loads((PROJECT / "config/quality-baseline-v4.json").read_text())
    return [
        {"role": "system", "content": str(frozen["system"])},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": question,
                    "evidence": [{"id": c.chunk_id, "quote": c.quote} for c in citations],
                }
            ),
        },
    ]


if __name__ == "__main__":
    worker.generation_messages = baseline_messages
    worker.main()
