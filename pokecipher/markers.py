"""Formatting of the markers the decoder emits for characters it cannot fully resolve.

Two distinct markers are used because the two situations are semantically
different, and downstream consumers (including the web UI) treat them
differently:

* **ambiguity** ``[x,y]`` — the decoder tracked state correctly, but the cipher
  itself is lossy here and several characters remain genuinely valid.
* **mismatch** ``{x,y}`` — no surviving branch could consume this token at all,
  so the ciphertext is very likely corrupted.
"""

from __future__ import annotations

from collections.abc import Iterable

AMBIGUITY_OPEN: str = "["
AMBIGUITY_CLOSE: str = "]"
MISMATCH_OPEN: str = "{"
MISMATCH_CLOSE: str = "}"
SEPARATOR: str = ","
UNRESOLVED: str = "<???>"


def format_ambiguity(chars: Iterable[str]) -> str:
    """Render an ambiguity marker listing every still-valid character."""
    return AMBIGUITY_OPEN + SEPARATOR.join(sorted(chars)) + AMBIGUITY_CLOSE


def format_mismatch(chars: Iterable[str]) -> str:
    """Render a state-mismatch marker listing every character the token could mean."""
    return MISMATCH_OPEN + SEPARATOR.join(sorted(chars)) + MISMATCH_CLOSE
