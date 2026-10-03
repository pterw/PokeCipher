"""Invariant and adversarial tests for the cipher core.

Complements the behavioural suites (``test_cipher.py``,
``test_cipher_pyramidal.py``, ``test_pokecipher_units.py``) with properties that
hold for *every* input, not just the examples pinned there:

* round-trip faithfulness for messages inside the decoder's branch budget;
* determinism of encode and decode;
* safe handling of malformed ``[CHAR:N]`` and legacy ``[err:...]`` tokens;
* the decoder's branch cap and branch deduplication;
* a seeded adversarial token-stream fuzz that must never crash the decoder or
  make it emit the internal ``<???>`` unresolved marker;
* an explicit pin on the branch budget's known limitation.

Known limitation (measured, not hypothetical)
---------------------------------------------
``MAX_DECODE_BRANCHES`` is a hard cap, and when the merged hypothesis count
exceeds it the branches dropped can include the true reading; the decode then
reports a wrong character with no marker. Measured on bracket-free prose (this
repository's own AGENTS.md with its notation characters removed): 58 of 4,000
positions (1.5%) decode wrongly-and-unmarked, and the budget is first exceeded
at roughly 50-60 characters of prose. Decoding is exact for every message
inside the budget, which covers the UI's examples and the legacy suites.

Marking the overflow was tried and rejected on measurement: deferring to a
``{x,y}`` marker desynchronises the occurrence counts, which both floods the
output (1,045 markers vs 62 on 4 kB of prose) and *increases* silently lost
positions (67 vs 58). A converged-first branch-selection policy was also tried
and did not improve the loss rate. Fixing this properly needs a better state
representation or an unbounded branch count, both outside this change's scope;
the tests below pin the boundary so any future fix is deliberate and visible.
"""

from __future__ import annotations

import random
import unittest

from pokecipher import (
    ASCII_MAX,
    ASCII_MIN,
    MAX_DECODE_BRANCHES,
    NAME_INDEX,
    decode_message,
    encode_message,
)
from pokecipher.decoder import Branch, fork, literal_for
from pokecipher.pokedex import lookup_name
from pokecipher.state import CharCounts
from pokecipher.tokens import parse_char_token

# Characters that would confuse the round-trip scanner: the decoder's marker
# notation uses them literally, so a decoded marker is indistinguishable from
# decoded plaintext containing them (the same documented limitation the
# frontend's markers.ts records). The invariant is asserted over the rest of
# the printable domain.
_MARKER_SYNTAX = set("[]{}<>")

_PRINTABLE_SAFE = "".join(
    chr(code) for code in range(ASCII_MIN, ASCII_MAX + 1) if chr(code) not in _MARKER_SYNTAX
)


def exceeds_branch_budget(encoded: str) -> bool:
    """True when decoding may have hit the branch cap.

    Conservative: a truncated fork returns exactly MAX_DECODE_BRANCHES branches,
    so never seeing that count proves no truncation happened. Used to keep only
    genuinely in-budget messages under the strict faithfulness assertion.
    """
    branches = [Branch.start()]
    for token in encoded.split():
        if literal_for(token) is not None:
            continue
        mappings = lookup_name(token)
        if mappings is None:
            continue
        nxt = fork(branches, tuple(mappings))
        if len(nxt) == MAX_DECODE_BRANCHES:
            return True
        branches = nxt or [branch.skipped() for branch in branches]
        if len(branches) == 1:
            branches = [Branch(branches[0].state)]
    return False


def read_marker(decoded: str, pos: int) -> tuple[list[str], int] | None:
    """Parse a ``[x,y]`` or ``{x,y}`` marker at ``pos`` grammar-wise.

    A regex cannot do this: a candidate may itself be a bracket character (the
    marker for ``]`` and ``i`` reads ``[],i]``), because every printable
    character is encodable. Reading candidate/comma/closer directly handles
    that. Returns the candidate list and the position after the marker.
    """
    opener = decoded[pos]
    if opener not in "[{":
        return None
    closer = "]" if opener == "[" else "}"
    candidates: list[str] = []
    j = pos + 1
    while j < len(decoded):
        candidates.append(decoded[j])
        j += 1
        if j < len(decoded) and decoded[j] == closer:
            return candidates, j + 1
        if j >= len(decoded) or decoded[j] != ",":
            return None
        j += 1
    return None


def check_faithful(case: unittest.TestCase, plaintext: str) -> None:
    """Assert decode(encode(plaintext)) loses no character.

    The cipher is deliberately lossy: cross-region name overlap means a decoded
    position can stay ambiguous (``[n,o]``). Faithfulness is the honest
    invariant — each position is either the original character or a marker
    listing it. Only valid inside the branch budget; see the module docstring.
    """
    decoded = decode_message(encode_message(plaintext))
    pos = 0
    for char in plaintext:
        with case.subTest(char=char, decoded=decoded):
            code = ord(char)
            if not ASCII_MIN <= code <= ASCII_MAX:
                # Non-printable characters pass through as literal tokens.
                case.assertTrue(decoded.startswith(char, pos))
                pos += 1
                continue
            if decoded.startswith(char, pos):
                pos += 1
                continue
            marker = read_marker(decoded, pos)
            case.assertIsNotNone(marker, f"lost {char!r} at {pos} in {decoded!r}")
            assert marker is not None  # for the type checker
            candidates, end = marker
            case.assertIn(char, candidates)
            pos = end
    case.assertEqual(pos, len(decoded), f"trailing garbage in {decoded!r}")


class RoundTripInvariantTests(unittest.TestCase):
    """Messages inside the branch budget decode faithfully, character for character."""

    CORPUS = (
        "",
        "Hi",
        "Hello World!",
        "I don't know",
        "test",
        "A" * 21,
        "banana",
        "Mississippi",
        "The quick brown fox jumps over the lazy dog.",
        "line one\nline two\r\nwith tab and bell\a",
    )

    def assertInBudget(self, plaintext: str) -> None:
        self.assertFalse(
            exceeds_branch_budget(encode_message(plaintext)),
            f"{plaintext!r} exceeds the branch budget; move it to the limitation test",
        )

    def test_every_safe_printable_character_round_trips(self):
        """Each printable character survives alone, where no state cycling occurs."""
        for char in _PRINTABLE_SAFE:
            with self.subTest(char=char):
                self.assertInBudget(char)
                check_faithful(self, char)

    def test_corpus_messages_round_trip_faithfully(self):
        """Reference messages stay inside the budget and lose nothing."""
        for message in self.CORPUS:
            with self.subTest(message=message[:24]):
                self.assertInBudget(message)
                check_faithful(self, message)

    def test_seeded_random_short_messages_round_trip_faithfully(self):
        """Deterministic random short messages stay in budget and lose nothing."""
        rng = random.Random(0xC1FEE)
        checked = 0
        for _ in range(300):
            message = "".join(rng.choice(_PRINTABLE_SAFE) for _ in range(rng.randrange(0, 31)))
            if exceeds_branch_budget(encode_message(message)):
                continue
            checked += 1
            with self.subTest(message=message):
                check_faithful(self, message)
        # Guard against the corpus silently emptying out if the budget shrinks.
        self.assertGreaterEqual(checked, 250)


class DeterminismTests(unittest.TestCase):
    """The same input always produces the same output from a fresh state."""

    MESSAGES = [
        "",
        "Hello World!",
        "A" * 40,
        "The quick brown fox jumps over the lazy dog. " * 10,
        "line\nbreak\rand\ttab",
    ]

    def test_encode_is_deterministic(self):
        """Encoding the same message twice yields identical ciphertext."""
        for message in self.MESSAGES:
            with self.subTest(message=message[:20]):
                self.assertEqual(encode_message(message), encode_message(message))

    def test_decode_is_deterministic(self):
        """Decoding the same ciphertext twice yields identical plaintext."""
        for message in self.MESSAGES:
            encoded = encode_message(message)
            with self.subTest(message=message[:20]):
                self.assertEqual(decode_message(encoded), decode_message(encoded))


class MalformedTokenTests(unittest.TestCase):
    """Malformed control tokens are reported, never crashed on or invented from."""

    def test_negative_char_token_is_invalid(self):
        """A negative code point cannot be a character."""
        self.assertIsNone(parse_char_token("[CHAR:-1]"))

    def test_overflow_char_token_is_invalid(self):
        """A code point past U+10FFFF cannot be a character."""
        self.assertIsNone(parse_char_token("[CHAR:1114112]"))

    def test_empty_char_token_is_invalid(self):
        """A [CHAR:] token with no number cannot be a character."""
        self.assertIsNone(parse_char_token("[CHAR:]"))

    def test_trailing_junk_char_token_is_invalid(self):
        """A [CHAR:N] token with trailing junk cannot be a character."""
        self.assertIsNone(parse_char_token("[CHAR:65]x"))

    def test_malformed_char_tokens_render_as_invalid_marker(self):
        """Undecodable [CHAR:] tokens become <?> in decoded output."""
        self.assertEqual(decode_message("Zubat [CHAR:abc]"), "H<?>")
        self.assertEqual(decode_message("Zubat [CHAR:-1]"), "H<?>")
        self.assertEqual(decode_message("Zubat [CHAR:1114112]"), "H<?>")

    def test_legacy_err_token_is_reported(self):
        """Historical [err:...] tokens decode to an explicit error marker."""
        self.assertEqual(
            decode_message("Zubat [err:idx_99_region_Kanto]"),
            "H<?error encoding: [err:idx_99_region_Kanto]>",
        )

    def test_unknown_names_are_reported_per_token(self):
        """Each unknown name gets its own marker; decoding continues past it."""
        self.assertEqual(decode_message("Zubat fakemon Weepinbell"), "H<?unknown: fakemon>e")


class EmptyAndWhitespaceTests(unittest.TestCase):
    """Degenerate inputs decode to degenerate outputs."""

    def test_whitespace_only_input_decodes_to_empty(self):
        """Whitespace splits to no tokens, so nothing is emitted."""
        self.assertEqual(decode_message("   \t  \n "), "")

    def test_only_special_tokens_decode_to_their_literals(self):
        """A stream of control tokens decodes without touching cipher state."""
        self.assertEqual(decode_message("[NEWLINE] [RETURN] [CHAR:9]"), "\n\r\t")


class BranchCapTests(unittest.TestCase):
    """fork() is the only place branches multiply, and it must respect the cap."""

    def test_fork_never_exceeds_the_branch_cap(self):
        """Forty divergent hypotheses are clamped to MAX_DECODE_BRANCHES."""
        branches = [Branch(CharCounts({f"c{i}": 1})) for i in range(40)]
        mappings = tuple((f"c{i}", 1) for i in range(40))
        self.assertEqual(len(fork(branches, mappings)), MAX_DECODE_BRANCHES)

    def test_fork_deduplicates_identical_states(self):
        """Branches that reach identical counts merge into one."""
        self.assertEqual(len(fork([Branch.start(), Branch.start()], (("a", 0),))), 1)

    def test_fork_dies_when_no_candidate_matches_state(self):
        """A token no branch can consume yields no follow-up branches."""
        # After one 'a', the next 'a' wants region 1; a region-0 mapping dies.
        self.assertEqual(fork([Branch.start().advanced("a")], (("a", 0),)), [])


class BranchBudgetLimitationTests(unittest.TestCase):
    """Pins the branch budget's known limitation (see the module docstring).

    These tests do not endorse the limitation; they make it visible, bounded,
    and impossible to change without a deliberate edit. If a future fix makes
    long messages exact, ``test_budget_is_exceeded_by_long_repetitive_input``
    is the test to update.
    """

    CORRUPTING_MESSAGE = "p'AHXM70pmLlHB9$9Ij_xVDJPKr\\q8aSmFYnC0v,@h0S`aH6,^"

    def test_budget_is_exceeded_by_long_repetitive_input(self):
        """A 50-character high-collision message does reach the cap."""
        self.assertTrue(exceeds_branch_budget(encode_message(self.CORRUPTING_MESSAGE)))

    def test_budget_is_not_exceeded_by_short_messages(self):
        """Everyday short messages stay inside the budget and are exact."""
        for message in ("Hello World!", "I don't know", "test", "PokeCipher"):
            with self.subTest(message=message):
                self.assertFalse(exceeds_branch_budget(encode_message(message)))

    def test_over_budget_decode_still_terminates_and_returns_text(self):
        """Past the budget the decode is best-effort, but it never fails."""
        decoded = decode_message(encode_message(self.CORRUPTING_MESSAGE))
        self.assertIsInstance(decoded, str)
        self.assertNotIn("<???>", decoded)
        self.assertGreaterEqual(len(decoded), len(self.CORRUPTING_MESSAGE) - 2)


class AdversarialFuzzTests(unittest.TestCase):
    """Seeded token soup must decode safely: no crash, no unresolved marker.

    ``<???>`` is the decoder's internal unresolved marker; every code path that
    can produce a Slot guarantees at least one candidate, so it must never
    reach the user. The seed makes the corpus deterministic.
    """

    def test_token_streams_fail_safely(self):
        """Two thousand random token streams decode without raising."""
        rng = random.Random(0xDEC0DE)
        names = list(NAME_INDEX)
        pool = (
            names
            + [name.lower() for name in names[:50]]
            + [name.upper() for name in names[:50]]
            + [
                "[NEWLINE]",
                "[RETURN]",
                "[CHAR:9]",
                "[CHAR:0]",
                "[CHAR:1114111]",
                "[CHAR:abc]",
                "[CHAR:-1]",
                "[CHAR:65]x",
                "[CHAR:",
                "[err:idx_99_region_Kanto]",
                "fakemon",
                "[n,o]",
                "{x,y}",
                "<?>",
                "]",
            ]
        )
        for _ in range(2000):
            stream = " ".join(rng.choice(pool) for _ in range(rng.randrange(0, 31)))
            with self.subTest(stream=stream):
                result = decode_message(stream)
                self.assertIsInstance(result, str)
                self.assertNotIn("<???>", result)


if __name__ == "__main__":
    unittest.main()
