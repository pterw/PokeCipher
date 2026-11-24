"""Formatting and parsing of the non-Pokémon tokens that appear in ciphertext.

Both directions live here so the encoder and the decoder can never drift apart
on token spelling. Nothing else in the package may spell a token literally.
"""

from __future__ import annotations

NEWLINE_TOKEN: str = "[NEWLINE]"
RETURN_TOKEN: str = "[RETURN]"
CHAR_TOKEN_PREFIX: str = "[CHAR:"
CHAR_TOKEN_SUFFIX: str = "]"
ERR_TOKEN_PREFIX: str = "[err:"
INVALID_CHAR_TOKEN: str = "<?>"
UNKNOWN_PREFIX: str = "<?unknown: "
UNKNOWN_SUFFIX: str = ">"
ERROR_PREFIX: str = "<?error encoding: "
ERROR_SUFFIX: str = ">"

#: Inclusive bounds of the Unicode surrogate range. Code points inside it are
#: representable in a Python ``str`` but cannot be encoded as UTF-8, so they are
#: not valid characters for a token to name.
SURROGATE_MIN: int = 0xD800
SURROGATE_MAX: int = 0xDFFF


def format_char_token(code_point: int) -> str:
    """Render a non-printable character as a ``[CHAR:N]`` token."""
    return f"{CHAR_TOKEN_PREFIX}{code_point}{CHAR_TOKEN_SUFFIX}"


def parse_char_token(token: str) -> str | None:
    """Return the character a ``[CHAR:N]`` token encodes, or ``None`` if unparseable.

    Only Unicode *scalar* values are accepted. ``chr`` will happily build the
    surrogate range 0xD800-0xDFFF, but those code points cannot be encoded as
    UTF-8, so a token naming one would decode into a string no HTTP response can
    serialise. Rejecting them here keeps the decoder total over its own
    vocabulary, which is the property the rest of the package relies on.
    """
    if not (token.startswith(CHAR_TOKEN_PREFIX) and token.endswith(CHAR_TOKEN_SUFFIX)):
        return None
    body = token[len(CHAR_TOKEN_PREFIX) : -len(CHAR_TOKEN_SUFFIX)]
    try:
        code_point = int(body)
        character = chr(code_point)
    except ValueError:
        return None
    if SURROGATE_MIN <= code_point <= SURROGATE_MAX:
        return None
    return character


def format_unknown(token: str) -> str:
    """Render a token that is not a known Pokémon name."""
    return f"{UNKNOWN_PREFIX}{token}{UNKNOWN_SUFFIX}"


def format_error_token(token: str) -> str:
    """Render a legacy ``[err:...]`` token as a decoder error marker.

    The current encoder cannot emit ``[err:...]`` tokens: every index it can
    produce lies inside the validated Pokédex bounds. They are recognised here
    only so that hand-written or historical ciphertext is reported clearly
    instead of being mistaken for an unknown Pokémon name.
    """
    return f"{ERROR_PREFIX}{token}{ERROR_SUFFIX}"
