import re
from dataclasses import dataclass

from pydantic import Field, ValidationError

from evidence_rag.contracts import Citation, StrictModel
from evidence_rag.models.fixture import tokens

STOPWORDS_REVISION = "stopwords-v1"
STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "which",
    "how",
    "does",
    "do",
    "did",
    "in",
    "of",
    "to",
    "for",
    "from",
    "with",
    "and",
    "or",
    "it",
    "its",
    "on",
    "as",
    "this",
    "that",
    "current",
    "active",
    "latest",
    "edition",
    "please",
    "give",
    "state",
    "identify",
    "report",
    "resolve",
    "name",
    "after",
    "remain",
    "remains",
    "still",
    "using",
    "exactly",
}
PROMPT_REVISION = "evidence-json-v3-bounded"
GENERATOR_REVISION = "extractive-sentences-v1"


@dataclass(frozen=True)
class Generated:
    text: str
    citations: list[Citation]
    abstained: bool
    reason: str | None


class StructuredGeneration(StrictModel):
    answer: str = Field(max_length=2000)
    cited_chunk_ids: list[str] = Field(max_length=5)
    insufficient_evidence: bool = Field(strict=True)


def extractive(question: str, citations: list[Citation]) -> Generated:
    terms = set(tokens(question)) - STOPWORDS
    required = min(2, len(terms))
    choices: list[tuple[int, int, int, str]] = []
    if not terms:
        return Generated("", [], True, "insufficient_evidence")
    for rank, citation in enumerate(citations):
        for sentence in re.finditer(r"[^.!?\n]+[.!?]?", citation.quote):
            text = sentence.group().strip()
            overlap = len(terms & set(tokens(text)))
            if overlap >= required:
                choices.append((-overlap, rank, sentence.start(), text))
    choices.sort()
    selected: list[Citation] = []
    parts: list[str] = []
    seen: set[str] = set()
    for _, rank, _, text in choices:
        if text in seen:
            continue
        citation = citations[rank]
        if citation not in selected:
            selected.append(citation)
        parts.append(f"{text} [{selected.index(citation) + 1}]")
        seen.add(text)
        if len(parts) == 3:
            break
    return Generated(
        "\n\n".join(parts), selected, not bool(parts), None if parts else "insufficient_evidence"
    )


def validate_generation(raw: str, citations: list[Citation]) -> Generated:
    try:
        result = StructuredGeneration.model_validate_json(raw)
        known = {c.chunk_id: c for c in citations}
        if any(key not in known for key in result.cited_chunk_ids):
            raise ValueError("Unknown source")
        if result.insufficient_evidence:
            return Generated("", [], True, "insufficient_evidence")
        if not result.answer.strip() or not result.cited_chunk_ids:
            raise ValueError("Missing evidence")
        return Generated(
            result.answer,
            [known[key] for key in dict.fromkeys(result.cited_chunk_ids)],
            False,
            None,
        )
    except (ValueError, ValidationError):
        return Generated("", [], True, "invalid_generation")
