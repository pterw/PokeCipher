"""Invariant constants for the PokéCipher codec.

This module is the leaf of the package: it must not import from anywhere else in
``pokecipher`` so that every other module can depend on it without cycles.
"""

ASCII_MIN: int = 32
"""Lowest encodable ASCII code point: the space character."""

ASCII_MAX: int = 126
"""Highest encodable ASCII code point: the tilde character."""

REGION_SIZE: int = ASCII_MAX - ASCII_MIN + 1
"""Number of Pokémon every regional Pokédex must supply (95)."""

MAX_DECODE_BRANCHES: int = 32
"""Upper bound on simultaneous decoder branches, bounding worst-case decode cost."""
