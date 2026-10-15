import hashlib
import re
from dataclasses import dataclass

CHUNKER_REVISION = "heading-window-v1"


@dataclass(frozen=True)
class Chunk:
    id: str
    version_id: str
    section_id: str
    start_char: int
    end_char: int
    text: str


def chunk_document(version_id: str, text: str) -> tuple[Chunk, ...]:
    if not text.strip() or "\x00" in text or re.search(r"<\s*script\b", text, re.IGNORECASE):
        raise ValueError("Invalid plain Markdown")
    text.encode("utf-8", errors="strict")
    headings = list(re.finditer(r"^#{1,6}\s+(.+)$", text, re.MULTILINE))
    if not headings or text[: headings[0].start()].strip():
        raise ValueError("Markdown must start with a heading")
    result: list[Chunk] = []
    seen: dict[str, int] = {}
    for i, heading in enumerate(headings):
        slug = re.sub(r"[^\w]+", "-", heading.group(1).lower()).strip("-")
        seen[slug] = seen.get(slug, 0) + 1
        section = slug if seen[slug] == 1 else f"{slug}-{seen[slug]}"
        limit = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        start = heading.start()
        while start < limit:
            words = list(re.finditer(r"\S+", text[start:limit]))
            end = min(limit, start + 1000)
            if len(words) > 160:
                end = min(end, start + words[159].end())
            fitting = [w for w in words if start + w.end() <= end]
            if (
                fitting
                and end < limit
                and text[end - 1 : end].isspace() is False
                and text[end : end + 1].isspace() is False
            ):
                end = start + fitting[-1].end()
            if end <= start:
                end = min(start + 1000, limit)
            payload = f"{version_id}:{section}:{start}:{end}:{CHUNKER_REVISION}"
            result.append(
                Chunk(
                    hashlib.sha256(payload.encode()).hexdigest(),
                    version_id,
                    section,
                    start,
                    end,
                    text[start:end],
                )
            )
            if end == limit:
                break
            covered = [w for w in words if start + w.end() <= end]
            next_start = start + covered[-32].start() if len(covered) > 32 else end
            start = next_start if next_start > start else end
    return tuple(result)
