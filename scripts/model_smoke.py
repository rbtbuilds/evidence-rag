import json
import time

from evidence_rag.answers.generation import PROMPT_REVISION
from evidence_rag.config import Settings
from evidence_rag.contracts import Citation
from evidence_rag.models.generation import GENERATION_SETTINGS
from evidence_rag.models.runner import ModelRunner


def main() -> None:
    runner = ModelRunner(Settings.from_env().root)
    begin = time.monotonic()
    with runner.session("real model smoke: embed rerank generate") as session:
        vectors = session.embed(["The circulation display limit is 35 units."])
        scores = session.rerank(
            "What is the circulation display limit?", ["The circulation display limit is 35 units."]
        )
        result = session.generate(
            "What is the circulation display limit?",
            [
                Citation(
                    chunk_id="smoke",
                    document_id="smoke",
                    version_id="smoke",
                    title="Smoke",
                    version_label="v2",
                    effective_date="2026-10-15",
                    section_id="circulation-overview",
                    start_char=0,
                    end_char=43,
                    quote="The circulation display limit is 35 units.",
                )
            ],
        )
        print(
            json.dumps(
                {
                    "execution_profile": "local",
                    "dimensions": len(vectors[0]),
                    "rerank_scores": scores,
                    "generation_output": result.output,
                    "generation_revision": result.revision,
                    "prompt_revision": PROMPT_REVISION,
                    "generation_settings": GENERATION_SETTINGS,
                    "output_tokens": result.output_tokens,
                    "hit_output_limit": result.hit_output_limit,
                    "embedding_truncations": session.embedding_truncations,
                    "elapsed_seconds": time.monotonic() - begin,
                }
            )
        )


if __name__ == "__main__":
    main()
