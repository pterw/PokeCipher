"""PokéCipher: a stateful polyalphabetic substitution cipher over Pokémon names.

Public surface
--------------
* :func:`encode_message` — plaintext → space-separated Pokémon names.
* :func:`decode_message` — Pokémon names → plaintext.
* :data:`decode_flexible_error_reporting` — historical alias of :func:`decode_message`.
* Pokédex data and lookup index, re-exported for callers that inspect them.
"""

from .constants import ASCII_MAX, ASCII_MIN, MAX_DECODE_BRANCHES, REGION_SIZE
from .decoder import decode_message
from .encoder import encode_message
from .pokedex import NAME_INDEX, NUM_REGIONS, REGION_LISTS, REGION_NAMES, REGIONS

#: Backwards-compatible alias for the decoder's original name.
decode_flexible_error_reporting = decode_message

__all__ = [
    "ASCII_MAX",
    "ASCII_MIN",
    "MAX_DECODE_BRANCHES",
    "NAME_INDEX",
    "NUM_REGIONS",
    "REGION_LISTS",
    "REGION_NAMES",
    "REGION_SIZE",
    "REGIONS",
    "decode_flexible_error_reporting",
    "decode_message",
    "encode_message",
]
