"""Immutable per-character occurrence counts: the cipher's only mutable-looking state."""

from __future__ import annotations


class CharCounts:
    """How many times each character has been seen so far.

    Instances are immutable. :meth:`advanced` returns a new object rather than
    mutating in place, which lets the decoder fork hypotheses cheaply without
    any risk of two branches aliasing the same counts.

    Callers ask this object questions (:meth:`count_of`, :meth:`region_index`)
    instead of reaching into an underlying dict, keeping the decoder free of
    knowledge about how the counts are stored.
    """

    __slots__ = ("_counts",)

    def __init__(self, counts: dict[str, int] | None = None) -> None:
        self._counts: dict[str, int] = dict(counts) if counts else {}

    @classmethod
    def empty(cls) -> CharCounts:
        """Return a fresh state in which nothing has been seen."""
        return cls()

    def count_of(self, char: str) -> int:
        """Return how many times ``char`` has been seen so far."""
        return self._counts.get(char, 0)

    def advanced(self, char: str) -> CharCounts:
        """Return a new state in which ``char`` has been seen once more."""
        nxt = dict(self._counts)
        nxt[char] = nxt.get(char, 0) + 1
        return CharCounts(nxt)

    def region_index(self, char: str, num_regions: int) -> int:
        """Return the region this next occurrence of ``char`` belongs to."""
        return self.count_of(char) % num_regions

    def identity(self) -> frozenset[tuple[str, int]]:
        """Return a hashable identity, used to merge equivalent decoder branches."""
        return frozenset(self._counts.items())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CharCounts):
            return NotImplemented
        return self._counts == other._counts

    def __hash__(self) -> int:
        return hash(self.identity())

    def __repr__(self) -> str:
        return f"CharCounts({self._counts!r})"
