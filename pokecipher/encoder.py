"""Plaintext → Pokémon-name encoding."""

from __future__ import annotations

from .constants import ASCII_MAX, ASCII_MIN
from .pokedex import NUM_REGIONS, REGION_LISTS
from .state import CharCounts
from .tokens import NEWLINE_TOKEN, RETURN_TOKEN, format_char_token


def encode_token(char: str) -> str:
    """Encode a single non-printable character as its ciphertext token."""
    if char == "\n":
        return NEWLINE_TOKEN
    if char == "\r":
        return RETURN_TOKEN
    return format_char_token(ord(char))


def encode_message(message: str) -> str:
    """Encode plaintext into a space-separated sequence of Pokémon names.

    Each printable ASCII character (codes 32-126) is normalised to an index
    (``ord(char) - 32``) and replaced by the Pokémon at that index in a regional
    Pokédex. Repeated characters cycle through the regions (Kanto → Johto →
    Hoenn → Kanto …) according to how many times that character has already
    appeared, so the same character rarely yields the same Pokémon twice.

    Characters outside the printable range are preserved as tokens rather than
    dropped: ``\\n`` becomes ``[NEWLINE]``, ``\\r`` becomes ``[RETURN]``, and
    anything else becomes ``[CHAR:N]`` using its code point.

    Every index the encoder can produce lies within the validated Pokédex
    bounds, so this function cannot fail on out-of-range input.
    """
    counts = CharCounts.empty()
    parts: list[str] = []

    for char in message:
        code = ord(char)
        if ASCII_MIN <= code <= ASCII_MAX:
            index = code - ASCII_MIN
            region = counts.region_index(char, NUM_REGIONS)
            counts = counts.advanced(char)
            parts.append(REGION_LISTS[region][index])
        else:
            parts.append(encode_token(char))

    return " ".join(parts)
