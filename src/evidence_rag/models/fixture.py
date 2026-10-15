import hashlib
import math
import re

TOKEN_REVISION = "unicode-words-v1"


def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower(), re.UNICODE)


class FixtureEmbedder:
    revision = "fixture-hash-v1"

    def embed(self, texts: list[str], *, is_query: bool = False) -> tuple[tuple[float, ...], ...]:
        result: list[tuple[float, ...]] = []
        for text in texts:
            vector = [0.0] * 384
            for token in tokens(text):
                digest = hashlib.sha256(token.encode()).digest()
                vector[int.from_bytes(digest[:4], "big") % 384] += 1 if digest[4] & 1 else -1
            norm = math.sqrt(sum(v * v for v in vector))
            if not norm:
                vector[0] = 1
                norm = 1
            result.append(tuple(v / norm for v in vector))
        return tuple(result)


class FixtureReranker:
    revision = "fixture-overlap-v1"

    def rerank(self, question: str, passages: list[str]) -> list[float]:
        query = set(tokens(question))
        return [float(len(query & set(tokens(text)))) for text in passages]
