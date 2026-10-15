import importlib
import json
from collections.abc import Callable
from typing import Protocol, cast

import pytest

from evidence_rag.models.generation import generation_schema
from tests.unit.test_generation import source


class Parser(Protocol):
    def get_allowed_characters(self) -> str: ...
    def add_character(self, character: str) -> "Parser": ...
    def can_end(self) -> bool: ...


def accepted(raw: str) -> bool:
    factory = cast(
        Callable[[dict[str, object]], Parser],
        importlib.import_module("lmformatenforcer").JsonSchemaParser,
    )
    parser = factory(generation_schema([source()]))
    for character in raw:
        if character not in parser.get_allowed_characters():
            return False
        parser = parser.add_character(character)
    return parser.can_end()


def test_schema_enforces_keys_types_known_ids_and_bounds() -> None:
    valid = {"answer": "35 units.", "cited_chunk_ids": ["known"], "insufficient_evidence": False}
    assert accepted(json.dumps(valid))
    assert not accepted(json.dumps({**valid, "cited_chunk_ids": ["knowm"]}))
    assert not accepted(json.dumps({**valid, "cited_chunk_ids": ["known"] * 6}))
    assert not accepted(json.dumps({**valid, "insufficient_evidence": "false"}))
    assert not accepted(json.dumps({**valid, "extra": "ignored"}))
    assert not accepted(json.dumps({**valid, "answer": "x" * 2001}))
    assert not accepted('{"answer":"35 units."}')
    assert not accepted(json.dumps(valid)[:-1])
    assert accepted('{"answer":"","cited_chunk_ids":[],"insufficient_evidence":true}')
    with pytest.raises(ValueError):
        generation_schema([])
