"""Pokémon names → plaintext decoding, using fork/merge multi-state tracking."""

from __future__ import annotations

from dataclasses import dataclass, field

from .constants import MAX_DECODE_BRANCHES
from .markers import UNRESOLVED, format_ambiguity, format_mismatch
from .pokedex import NAME_INDEX, NUM_REGIONS
from .state import CharCounts
from .tokens import (
    CHAR_TOKEN_PREFIX,
    ERR_TOKEN_PREFIX,
    INVALID_CHAR_TOKEN,
    NEWLINE_TOKEN,
    RETURN_TOKEN,
    format_error_token,
    format_unknown,
    parse_char_token,
)

Mapping = tuple[str, int]


@dataclass(frozen=True)
class Branch:
    """One plausible decoding hypothesis.

    ``choices[i]`` holds every character the branch could have selected at
    Pokémon position ``i``. When two hypotheses reach identical counts they are
    merged by unioning their choices, which is what lets a later token
    retroactively resolve an earlier ambiguity.
    """

    state: CharCounts
    choices: tuple[frozenset[str], ...] = field(default_factory=tuple)

    @classmethod
    def start(cls) -> Branch:
        """Return the initial branch: nothing seen, nothing chosen."""
        return cls(CharCounts.empty())

    def candidates(self, mappings: tuple[Mapping, ...]) -> tuple[str, ...]:
        """Return the characters this branch could validly consume next."""
        return tuple(
            char
            for char, region in mappings
            if self.state.region_index(char, NUM_REGIONS) == region
        )

    def advanced(self, char: str) -> Branch:
        """Return a copy that has consumed ``char``."""
        return Branch(self.state.advanced(char), self.choices + (frozenset({char}),))

    def skipped(self) -> Branch:
        """Return a copy that consumed an uninterpretable token, keeping state."""
        return Branch(self.state, self.choices + (frozenset(),))

    def merged_with(self, other: Branch) -> Branch:
        """Return a branch combining both hypotheses' choices, position by position.

        Merging only ever happens between branches advanced at the same token,
        so the choice sequences always line up; ``strict=True`` turns that
        assumption into a checked invariant rather than a silent truncation.
        """
        return Branch(
            self.state,
            tuple(a | b for a, b in zip(self.choices, other.choices, strict=True)),
        )


@dataclass(frozen=True)
class Literal:
    """A run of output text that needs no further resolution."""

    text: str


@dataclass(frozen=True)
class Slot:
    """A placeholder resolved at render time from the surviving branches."""

    position: int


@dataclass(frozen=True)
class Mismatch:
    """A token no surviving branch could consume."""

    candidates: tuple[str, ...]


Segment = Literal | Slot | Mismatch


def literal_for(token: str) -> str | None:
    """Return the literal text a special token stands for, or ``None`` if it is not one."""
    if token == NEWLINE_TOKEN:
        return "\n"
    if token == RETURN_TOKEN:
        return "\r"
    if token.startswith(CHAR_TOKEN_PREFIX):
        parsed = parse_char_token(token)
        return parsed if parsed is not None else INVALID_CHAR_TOKEN
    if token.startswith(ERR_TOKEN_PREFIX):
        return format_error_token(token)
    return None


def fork(branches: list[Branch], mappings: tuple[Mapping, ...]) -> list[Branch]:
    """Advance every branch across every valid candidate, merging equivalent results."""
    merged: dict[frozenset[tuple[str, int]], Branch] = {}

    for branch in branches:
        for char in branch.candidates(mappings):
            advanced = branch.advanced(char)
            key = advanced.state.identity()
            if key in merged:
                merged[key] = merged[key].merged_with(advanced)
            else:
                merged[key] = advanced

    return list(merged.values())[:MAX_DECODE_BRANCHES]


def resolve(position: int, branches: list[Branch]) -> str:
    """Render one Pokémon position from the characters the live branches chose."""
    chars: set[str] = set()
    for branch in branches:
        if position < len(branch.choices):
            chars |= branch.choices[position]

    if len(chars) == 1:
        return next(iter(chars))
    if chars:
        return format_ambiguity(chars)
    return UNRESOLVED


def render(segments: list[Segment], branches: list[Branch]) -> str:
    """Turn a decode plan plus the surviving branches into the final plaintext."""
    parts: list[str] = []
    for segment in segments:
        if isinstance(segment, Literal):
            parts.append(segment.text)
        elif isinstance(segment, Mismatch):
            parts.append(format_mismatch(segment.candidates))
        else:
            parts.append(resolve(segment.position, branches))
    return "".join(parts)


def decode_message(encoded_pokemon_string: str) -> str:
    """Decode a Pokémon-name sequence back to plaintext.

    Decoding is *fork-based*: whenever a token is ambiguous the decoder spawns
    one branch per candidate character and advances each independently. Branches
    that reach identical counts are merged, and branches that become impossible
    simply die. Because of this, an ambiguity no longer poisons every later
    position — a following token frequently kills all but one branch, which
    retroactively resolves the earlier position.

    Output notation
    ---------------
    * a bare character — decoded unambiguously across all surviving branches;
    * ``[x,y]`` — genuine ambiguity: several characters remain valid even after
      the whole sequence was processed;
    * ``{x,y}`` — state mismatch: no branch could consume this token at all, so
      the candidates are listed ignoring state. This usually means corrupted
      ciphertext.
    * ``<?unknown: X>`` — ``X`` is not a known Pokémon name.
    * ``<?error encoding: X>`` — ``X`` is a legacy ``[err:...]`` token. The current
      encoder cannot produce these, but historical ciphertext is still reported.

    Positions are emitted as soon as they are final, which keeps retained history
    short and decoding close to linear on unambiguous input.
    """
    branches = [Branch.start()]
    emitted: list[str] = []
    pending: list[Segment] = []

    for token in encoded_pokemon_string.split():
        literal = literal_for(token)
        if literal is not None:
            pending.append(Literal(literal))
            continue

        mappings = NAME_INDEX.get(token)
        if mappings is None:
            pending.append(Literal(format_unknown(token)))
            continue

        next_branches = fork(branches, tuple(mappings))
        if next_branches:
            branches = next_branches
            pending.append(Slot(len(branches[0].choices) - 1))
        else:
            candidates = tuple(sorted({char for char, _region in mappings}))
            pending.append(Mismatch(candidates))
            branches = [branch.skipped() for branch in branches]

        # Every live branch is advanced or skipped together, so they all share one
        # choice length. A lone branch makes the whole backlog final: any future
        # branch descends from it, so its history is every future's prefix.
        if len(branches) == 1:
            emitted.append(render(pending, branches))
            pending.clear()
            branches = [Branch(branches[0].state)]

    emitted.append(render(pending, branches))
    return "".join(emitted)
