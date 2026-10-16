import pytest

from evidence_rag.models.decoding import allowed_tokens, build_tokenizer_data, core
from evidence_rag.models.generation import generation_schema
from tests.unit.test_generation import source


class AsciiTokenizer:
    def __init__(self) -> None:
        self.all_special_ids: list[int] = [0]

    eos_token_id: int = 0

    def __len__(self) -> int:
        return 128

    def encode(self, text: str, **kwargs: object) -> list[int]:
        return [ord(c) for c in text]

    def decode(self, ids: list[int], **kwargs: object) -> str:
        return "".join(chr(i) for i in ids)


class Sequence:
    def __init__(self, ids: list[int]) -> None:
        self.ids = ids

    def tolist(self) -> list[int]:
        return self.ids


def test_token_bridge_enforces_actual_prefixes_and_is_request_local() -> None:
    tokenizer = AsciiTokenizer()
    data = build_tokenizer_data(tokenizer)
    schema = generation_schema([source()])
    prefix = allowed_tokens(data, core("JsonSchemaParser")(schema))
    ids = [65, 66]
    text = '{"answer":"35 units.","cited_chunk_ids":["known"],"insufficient_evidence":false}'
    for char in text:
        choices = prefix(0, Sequence(ids))
        if text[: len(ids) - 2].endswith('["k'):
            assert ord("x") not in choices
        assert ord(char) in choices
        ids.append(ord(char))
    assert tokenizer.eos_token_id in prefix(0, Sequence(ids))
    other = source().model_copy(update={"chunk_id": "other"})
    fresh = allowed_tokens(data, core("JsonSchemaParser")(generation_schema([other])))
    ids = [65, 66]
    for char in text.split("known")[0]:
        assert ord(char) in fresh(0, Sequence(ids))
        ids.append(ord(char))
    assert ord("k") not in fresh(0, Sequence(ids))
    assert ord("o") in fresh(0, Sequence(ids))


def test_bridge_preserves_explicit_parser_settings(monkeypatch: object) -> None:
    from typing import Protocol, cast

    class Configured(Protocol):
        config: object

    data = build_tokenizer_data(AsciiTokenizer())
    config = core("CharacterLevelParserConfig")(
        alphabet="abc",
        force_json_field_order=False,
        max_consecutive_whitespaces=2,
        max_json_array_length=5,
    )
    parser = core("JsonSchemaParser")(generation_schema([source()]), config=config)
    allowed_tokens(data, parser)
    assert cast(Configured, parser).config is config


class ByteTokenizer:
    def __init__(self) -> None:
        self.all_special_ids: list[int] = [256]
        self.eos_token_id: int = 256

    def __len__(self) -> int:
        return 257

    def encode(self, text: str, **kwargs: object) -> list[int]:
        return list(text.encode("utf-8"))

    def decode(self, ids: list[int], **kwargs: object) -> str:
        return bytes(ids).decode("utf-8", errors="replace")


def test_byte_assembled_unicode_and_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    from evidence_rag.models.decoding import tokenizer_alphabet
    from evidence_rag.models.generation import generation_alphabet

    monkeypatch.setenv("LMFE_STRICT_JSON_FIELD_ORDER", "true")
    monkeypatch.setenv("LMFE_MAX_CONSECUTIVE_WHITESPACES", "0")
    tokenizer = ByteTokenizer()
    data = build_tokenizer_data(tokenizer)
    assert "🛰" not in tokenizer_alphabet(data)
    quote = source().model_copy(update={"quote": "The marker is 🛰𐐷."})
    config = core("CharacterLevelParserConfig")(
        alphabet=generation_alphabet(tokenizer_alphabet(data), "marker?", [quote]),
        force_json_field_order=False,
        max_consecutive_whitespaces=12,
        max_json_array_length=5,
    )
    parser = core("JsonSchemaParser")(generation_schema([quote]), config=config)
    prefix = allowed_tokens(data, parser)
    ids = [65, 66]
    text = '{"insufficient_evidence":false, "answer":"🛰𐐷", "cited_chunk_ids":["known"]}'
    for token in tokenizer.encode(text):
        assert token in prefix(0, Sequence(ids))
        ids.append(token)
    assert tokenizer.eos_token_id in prefix(0, Sequence(ids))


def test_decoding_bounds_answer_text_without_loosening_ids() -> None:
    data = build_tokenizer_data(AsciiTokenizer())
    prefix = allowed_tokens(data, core("JsonSchemaParser")(generation_schema([source()])))
    ids = [65, 66]
    text = '{"answer":"' + "a" * 180
    for char in text:
        assert ord(char) in prefix(0, Sequence(ids))
        ids.append(ord(char))
    choices = prefix(0, Sequence(ids))
    assert ord('"') in choices
    assert ord("a") not in choices
