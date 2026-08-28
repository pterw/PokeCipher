"""Exception types raised by the PokéCipher package."""


class PokeCipherError(Exception):
    """Base class for every error raised deliberately by this package."""


class PokedexError(PokeCipherError):
    """Raised when regional Pokédex data is structurally invalid.

    Raised at import time so a malformed Pokédex fails immediately rather than
    producing silently wrong ciphertext later on.
    """
