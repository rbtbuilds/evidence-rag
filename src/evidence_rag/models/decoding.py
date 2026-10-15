"""Bridge the LM Format Enforcer core to the current Transformers prefix callback.

The upstream 0.11.3 Transformers adapter imports a removed Transformers 4 symbol.
This uses its documented core API and tokenizer conversion algorithm (MIT).
"""

import importlib
from collections.abc import Callable
from typing import Protocol, cast


class DecodingTokenizer(Protocol):
    all_special_ids: list[int]
    eos_token_id: int

    def __len__(self) -> int: ...
    def encode(self, text: str, **kwargs: object) -> list[int]: ...
    def decode(self, ids: list[int], **kwargs: object) -> str: ...


class TokenSequence(Protocol):
    def tolist(self) -> list[int]: ...


class AllowedTokens(Protocol):
    allowed_tokens: list[int]


class Enforcer(Protocol):
    def get_allowed_tokens(self, ids: list[int]) -> AllowedTokens: ...


class Parser(Protocol):
    config: object


class TokenizerData(Protocol):
    tokenizer_alphabet: str


def core(name: str) -> Callable[..., object]:
    return cast(Callable[..., object], getattr(importlib.import_module("lmformatenforcer"), name))


def build_tokenizer_data(tokenizer: DecodingTokenizer) -> object:
    zero = tokenizer.encode("0", add_special_tokens=False)[-1]
    special = set(tokenizer.all_special_ids)
    tokens: list[tuple[int, str, bool]] = []
    for index in range(len(tokenizer)):
        if index in special:
            continue
        after_zero = tokenizer.decode([zero, index], clean_up_tokenization_spaces=False)[1:]
        standalone = tokenizer.decode([index], clean_up_tokenization_spaces=False)
        tokens.append((index, after_zero, len(after_zero) > len(standalone)))

    def decode(ids: list[int]) -> str:
        return tokenizer.decode(ids, clean_up_tokenization_spaces=False).rstrip("\ufffd")

    return core("TokenEnforcerTokenizerData")(
        tokens, decode, tokenizer.eos_token_id, False, len(tokenizer)
    )


def allowed_tokens(data: object, parser: object) -> Callable[[int, TokenSequence], list[int]]:
    configured = cast(Parser, parser)
    settings = configured.config
    enforcer = cast(Enforcer, core("TokenEnforcer")(data, parser))
    # Upstream replaces this with environment defaults in its constructor.
    configured.config = settings

    def prefix(_batch_id: int, sent: TokenSequence) -> list[int]:
        return enforcer.get_allowed_tokens(sent.tolist()).allowed_tokens

    return prefix


def tokenizer_alphabet(data: object) -> str:
    return cast(TokenizerData, data).tokenizer_alphabet
