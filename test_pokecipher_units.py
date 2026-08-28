"""Unit tests for the ``pokecipher`` package and the audit's coverage gaps.

Complements ``test_cipher.py`` and ``test_cipher_pyramidal.py``, which pin the
historical public contract. This file covers the modules that did not exist
before the package split, plus the gaps called out in AUDIT.md §6:

* 6.1 — lookup-table precomputation
* 6.2 — non-printable and out-of-range characters
* 6.3 — very long / high-repeat inputs and region wraparound
* 6.4 — performance and smoke tests
"""

import time
import unittest

from pokecipher import (
    ASCII_MAX,
    ASCII_MIN,
    MAX_DECODE_BRANCHES,
    NAME_INDEX,
    NUM_REGIONS,
    REGION_LISTS,
    REGION_NAMES,
    REGION_SIZE,
    REGIONS,
    decode_message,
    encode_message,
)
from pokecipher.decoder import Branch, Mismatch, Slot, fork, literal_for, render, resolve
from pokecipher.errors import PokedexError
from pokecipher.markers import format_ambiguity, format_mismatch
from pokecipher.pokedex import build_name_index, validate_regions
from pokecipher.state import CharCounts
from pokecipher.tokens import (
    CHAR_TOKEN_PREFIX,
    NEWLINE_TOKEN,
    RETURN_TOKEN,
    format_char_token,
    parse_char_token,
)


class TestLookupTable(unittest.TestCase):
    """Audit 6.1: the name → (char, region) lookup table is built correctly."""

    def test_every_region_contributes_region_size_entries(self):
        """Each region contributes exactly REGION_SIZE entries to the index."""
        total = sum(len(mappings) for mappings in NAME_INDEX.values())
        self.assertEqual(total, REGION_SIZE * NUM_REGIONS)

    def test_regions_are_indexed_in_order(self):
        """Region indices follow REGION_NAMES order."""
        self.assertEqual(REGION_NAMES, ["Kanto", "Johto", "Hoenn"])
        for region_index, region_name in enumerate(REGION_NAMES):
            first = REGIONS[region_name][0]
            self.assertIn((chr(ASCII_MIN), region_index), NAME_INDEX[first])

    def test_last_printable_character_maps_to_last_pokemon(self):
        """Tilde (index 94) maps to the 95th Pokémon of each region."""
        for region_index, region_name in enumerate(REGION_NAMES):
            last = REGIONS[region_name][REGION_SIZE - 1]
            self.assertIn((chr(ASCII_MAX), region_index), NAME_INDEX[last])

    def test_overlapping_names_accumulate_several_mappings(self):
        """A name appearing in several regions accumulates one mapping per region."""
        self.assertEqual(NAME_INDEX["Geodude"], [("i", 0), ("A", 1), ("X", 2)])
        self.assertEqual(NAME_INDEX["Slowpoke"], [("n", 0), ("o", 1)])

    def test_names_are_unique_within_a_region(self):
        """No region contains a duplicate name, so mappings never collide internally."""
        for region_name, pokemon in REGIONS.items():
            with self.subTest(region=region_name):
                self.assertEqual(len(pokemon), len(set(pokemon)))

    def test_build_name_index_orders_regions_and_accumulates_shares(self):
        """build_name_index indexes the first REGION_SIZE entries, in region order."""
        kanto = tuple(f"k{i}" for i in range(REGION_SIZE))
        # Region B reuses region A's first name, producing a shared mapping.
        johto = ("k0",) + tuple(f"j{i}" for i in range(1, REGION_SIZE))
        index = build_name_index({"A": kanto, "B": johto}, ["A", "B"])

        self.assertEqual(index["k0"], [(chr(ASCII_MIN), 0), (chr(ASCII_MIN), 1)])
        self.assertEqual(index["k1"], [(chr(ASCII_MIN + 1), 0)])
        self.assertEqual(index["j1"], [(chr(ASCII_MIN + 1), 1)])


class TestPokedexValidation(unittest.TestCase):
    """Fail-fast validation of Pokédex data."""

    def _valid(self):
        return {"R": tuple(f"p{i}" for i in range(REGION_SIZE))}

    def test_valid_data_passes(self):
        """Well-formed data validates without raising."""
        self.assertIsNone(validate_regions(self._valid(), ["R"]))

    def test_empty_region_list_raises(self):
        """An empty REGION_NAMES list raises PokedexError."""
        with self.assertRaises(PokedexError):
            validate_regions(self._valid(), [])

    def test_short_region_raises(self):
        """A region shorter than REGION_SIZE raises PokedexError."""
        with self.assertRaises(PokedexError):
            validate_regions({"R": ("p1", "p2")}, ["R"])

    def test_duplicate_name_within_region_raises(self):
        """A duplicate inside one region raises PokedexError."""
        regions = {"R": ("dup", *[f"p{i}" for i in range(REGION_SIZE - 2)], "dup")}
        self.assertEqual(len(regions["R"]), REGION_SIZE)
        with self.assertRaises(PokedexError):
            validate_regions(regions, ["R"])

    def test_blank_name_raises(self):
        """A blank or untrimmed name raises PokedexError."""
        regions = {"R": tuple(["  "] + [f"p{i}" for i in range(REGION_SIZE - 1)])}
        with self.assertRaises(PokedexError):
            validate_regions(regions, ["R"])

    def test_region_name_without_data_raises(self):
        """A name in REGION_NAMES with no matching data raises PokedexError."""
        with self.assertRaises(PokedexError):
            validate_regions(self._valid(), ["Missing"])

    def test_shipped_data_is_valid(self):
        """The Pokédex actually shipped by the package passes its own validation."""
        self.assertIsNone(validate_regions(REGIONS, REGION_NAMES))


class TestCharCounts(unittest.TestCase):
    """Immutable per-character occurrence counts."""

    def test_empty_counts_start_at_zero(self):
        """A fresh state reports zero for any character."""
        self.assertEqual(CharCounts.empty().count_of("a"), 0)

    def test_advanced_returns_a_new_object(self):
        """advanced() does not mutate the original state."""
        state = CharCounts.empty()
        nxt = state.advanced("a")
        self.assertEqual(state.count_of("a"), 0)
        self.assertEqual(nxt.count_of("a"), 1)

    def test_region_index_cycles(self):
        """region_index is the occurrence count modulo the region count."""
        state = CharCounts.empty()
        expected = []
        for _ in range(4):
            expected.append(state.region_index("a", NUM_REGIONS))
            state = state.advanced("a")
        self.assertEqual(expected, [0, 1, 2, 0])

    def test_equal_states_have_the_same_identity(self):
        """States built by the same advances compare and hash equal."""
        left = CharCounts.empty().advanced("a").advanced("b")
        right = CharCounts.empty().advanced("b").advanced("a")
        self.assertEqual(left, right)
        self.assertEqual(left.identity(), right.identity())
        self.assertEqual(hash(left), hash(right))

    def test_different_states_are_not_equal(self):
        """States with different counts are unequal."""
        self.assertNotEqual(CharCounts.empty().advanced("a"), CharCounts.empty())


class TestTokens(unittest.TestCase):
    """Token spelling and parsing."""

    def test_char_token_round_trip(self):
        """format_char_token and parse_char_token invert each other."""
        for code in (0, 9, 127, 233, 8364):
            with self.subTest(code=code):
                token = format_char_token(code)
                self.assertTrue(token.startswith(CHAR_TOKEN_PREFIX))
                self.assertEqual(parse_char_token(token), chr(code))

    def test_malformed_char_token_returns_none(self):
        """A [CHAR:] token with junk or truncated content does not parse."""
        self.assertIsNone(parse_char_token("[CHAR:abc]"))
        self.assertIsNone(parse_char_token("[CHAR:"))
        self.assertIsNone(parse_char_token("[CHAR:9"))

    def test_literals_for_special_tokens(self):
        """Special tokens decode to their literal characters."""
        self.assertEqual(literal_for(NEWLINE_TOKEN), "\n")
        self.assertEqual(literal_for(RETURN_TOKEN), "\r")

    def test_unparseable_char_token_becomes_invalid_marker(self):
        """A malformed [CHAR:] token renders as <?>."""
        self.assertEqual(literal_for("[CHAR:abc]"), "<?>")

    def test_non_special_token_returns_none(self):
        """A Pokémon name is not a special token."""
        self.assertIsNone(literal_for("Pikachu"))


class TestMarkers(unittest.TestCase):
    """Ambiguity and mismatch marker formatting."""

    def test_ambiguity_marker_is_sorted_and_bracketed(self):
        """Ambiguity markers use square brackets and sorted candidates."""
        self.assertEqual(format_ambiguity(["o", "n"]), "[n,o]")

    def test_mismatch_marker_is_sorted_and_braced(self):
        """Mismatch markers use curly braces and sorted candidates."""
        self.assertEqual(format_mismatch(["R", "n"]), "{R,n}")

    def test_the_two_markers_are_distinguishable(self):
        """Ambiguity and mismatch markers never look alike."""
        self.assertNotEqual(format_ambiguity(["n", "o"]), format_mismatch(["n", "o"]))


class TestBranchMechanics(unittest.TestCase):
    """The decoder's fork/merge branch engine."""

    def test_start_branch_has_no_choices(self):
        """A fresh branch has consumed nothing."""
        self.assertEqual(Branch.start().choices, ())

    def test_advanced_records_the_choice(self):
        """advanced() appends the consumed character as a choice set."""
        branch = Branch.start().advanced("a")
        self.assertEqual(branch.choices, (frozenset({"a"}),))
        self.assertEqual(branch.state.count_of("a"), 1)

    def test_skipped_records_an_empty_choice(self):
        """skipped() keeps position alignment without committing a character."""
        self.assertEqual(Branch.start().skipped().choices, (frozenset(),))

    def test_merge_unions_choices_position_wise(self):
        """Merging two branches unions their choices at every position."""
        left = Branch.start().advanced("a").advanced("b")
        right = Branch.start().advanced("a").advanced("c")
        self.assertEqual(
            left.merged_with(right).choices,
            (frozenset({"a"}), frozenset({"b", "c"})),
        )

    def test_candidates_respect_state(self):
        """Only characters whose expected region matches the state are candidates."""
        branch = Branch.start().advanced("a")  # next 'a' wants region 1, 'b' wants region 0
        self.assertEqual(branch.candidates((("a", 1), ("b", 2))), ("a",))
        self.assertEqual(branch.candidates((("a", 0), ("b", 0))), ("b",))

    def test_fork_caps_the_branch_count(self):
        """fork() never returns more than MAX_DECODE_BRANCHES branches."""
        mappings = tuple((chr(ASCII_MIN + i), 0) for i in range(REGION_SIZE))
        self.assertLessEqual(len(fork([Branch.start()], mappings)), MAX_DECODE_BRANCHES)

    def test_resolve_reports_ambiguity_when_branches_disagree(self):
        """resolve() renders [x,y] when surviving branches chose differently."""
        left = Branch.start().advanced("n")
        right = Branch.start().advanced("o")
        self.assertEqual(resolve(0, [left, right]), "[n,o]")

    def test_render_concatenates_all_segment_kinds(self):
        """render() handles slot and mismatch segments in one pass."""
        branch = Branch.start().advanced("a")
        self.assertEqual(render([Slot(0), Mismatch(("x", "y"))], [branch]), "a{x,y}")


class TestNonPrintableCharacters(unittest.TestCase):
    """Audit 6.2: characters outside the printable ASCII range."""

    def test_tab_encodes_to_char_token(self):
        """A tab encodes to [CHAR:9] and decodes back to a tab."""
        self.assertEqual(encode_message("\t"), "[CHAR:9]")
        self.assertEqual(decode_message("[CHAR:9]"), "\t")

    def test_newline_and_return_tokens(self):
        """Newline and carriage return use named tokens."""
        self.assertEqual(encode_message("\n"), NEWLINE_TOKEN)
        self.assertEqual(encode_message("\r"), RETURN_TOKEN)
        self.assertEqual(decode_message(NEWLINE_TOKEN), "\n")
        self.assertEqual(decode_message(RETURN_TOKEN), "\r")

    def test_unicode_above_ascii_round_trips(self):
        """Characters above ASCII 126 round-trip through [CHAR:N]."""
        for char in ("é", "€", "\U0001f600"):
            with self.subTest(char=char):
                encoded = encode_message(char)
                self.assertTrue(encoded.startswith(CHAR_TOKEN_PREFIX))
                self.assertEqual(decode_message(encoded), char)

    def test_mixed_content_round_trips(self):
        """Printable text, tabs, and newlines round-trip together."""
        original = "a\tb\nc\rd"
        self.assertEqual(decode_message(encode_message(original)), original)

    def test_control_characters_round_trip(self):
        """Control characters round-trip as [CHAR:N] tokens."""
        for code in (0, 1, 7, 27, 127):
            with self.subTest(code=code):
                char = chr(code)
                self.assertEqual(decode_message(encode_message(char)), char)


class TestRegionWraparound(unittest.TestCase):
    """Audit 6.3: region cycling wraps after visiting every region."""

    def test_seven_repeats_cycle_through_all_regions_twice(self):
        """Occurrences 1-7 use regions 0,1,2,0,1,2,0."""
        tokens = encode_message("A" * 7).split()
        self.assertEqual(len(tokens), 7)
        self.assertEqual(tokens[0], tokens[3])
        self.assertEqual(tokens[0], tokens[6])
        self.assertEqual(tokens[1], tokens[4])
        self.assertEqual(tokens[2], tokens[5])
        self.assertEqual(len({tokens[0], tokens[1], tokens[2]}), 3)

    def test_wraparound_matches_direct_region_lookup(self):
        """The Nth occurrence uses region N % 3 at the character's index."""
        index = ord("A") - ASCII_MIN
        tokens = encode_message("A" * 9).split()
        for occurrence, token in enumerate(tokens):
            self.assertEqual(token, REGION_LISTS[occurrence % NUM_REGIONS][index])

    def test_independent_characters_do_not_share_state(self):
        """Interleaving other characters does not disturb a character's own cycling."""
        solo = encode_message("aaa").split()
        interleaved = encode_message("axaxa").split()
        self.assertEqual(interleaved[0::2], solo)

    def test_long_repeat_run_decodes(self):
        """A long run of one character decodes without raising."""
        result = decode_message(encode_message("z" * 200))
        self.assertIsInstance(result, str)
        self.assertTrue(result)


class TestEncoderBounds(unittest.TestCase):
    """The encoder cannot address an index outside the Pokédex."""

    def test_all_printable_ascii_never_emits_err_token(self):
        """Encoding every printable character produces no [err:...] token."""
        printable = "".join(chr(code) for code in range(ASCII_MIN, ASCII_MAX + 1))
        self.assertNotIn("[err:", encode_message(printable))

    def test_every_region_covers_the_full_index_range(self):
        """Every index the encoder can produce exists in every region."""
        for region in REGION_LISTS:
            self.assertGreaterEqual(len(region), REGION_SIZE)


class TestPerformanceAndSmoke(unittest.TestCase):
    """Audit 6.4: performance and smoke behaviour on large inputs.

    The decoder emits each position as soon as it is final, so cost stays close
    to linear while branches keep collapsing to one. Measured on CPython 3.13:
    ~1.2 s for 10,000 characters of prose and ~0.05 s for 8,000 repeats of a
    single character. The pathological case is text that sustains an unresolved
    ambiguity for its entire length, which cannot collapse and stays quadratic
    (~3.3 s at 4,100 characters) — the reason the HTTP layer caps input.
    """

    # Varied prose: many distinct sentences, so ambiguities resolve and branches
    # collapse, which is what real messages look like.
    PROSE = (
        "The quick brown fox jumps over the lazy dog. "
        "A wizard's job is to vex chumps quickly in fog. "
        "Sphinx of black quartz, judge my vow. "
        "How vexingly quick daft zebras jump. "
        "Bright vixens jump; dozy fowl quack. "
        "Jaded zombies acted quaintly but kept driving. "
        "Five quacking zephyrs jolt my wax bed. "
        "Amazingly few discotheques provide jukeboxes. "
    ) * 40

    def test_encode_ten_thousand_characters_is_fast(self):
        """Encoding 10,000 characters stays well under two seconds."""
        message = "The quick brown fox jumps over the lazy dog. 0123456789! " * 180
        self.assertGreaterEqual(len(message), 10_000)
        start = time.perf_counter()
        encoded = encode_message(message)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 2.0)
        self.assertEqual(len(encoded.split()), len(message))

    def test_decode_ten_thousand_characters_of_prose_is_fast(self):
        """Decoding 10,000 characters of prose stays within the latency budget."""
        message = self.PROSE[:10_000]
        self.assertGreaterEqual(len(message), 10_000)
        encoded = encode_message(message)
        start = time.perf_counter()
        result = decode_message(encoded)
        elapsed = time.perf_counter() - start
        self.assertIsInstance(result, str)
        self.assertLess(elapsed, 5.0)

    def test_repeated_single_character_stays_linear(self):
        """A long run of one character stays cheap: one branch, early emission."""
        encoded = encode_message("z" * 8_000)
        start = time.perf_counter()
        result = decode_message(encoded)
        elapsed = time.perf_counter() - start
        self.assertIsInstance(result, str)
        self.assertLess(elapsed, 2.0)

    def test_highly_repetitive_input_stays_bounded(self):
        """Branch pruning keeps a long repetitive message tractable."""
        encoded = encode_message("ab" * 2000)
        start = time.perf_counter()
        result = decode_message(encoded)
        elapsed = time.perf_counter() - start
        self.assertIsInstance(result, str)
        self.assertLess(elapsed, 15.0)

    def test_prose_decoding_scales_near_linearly(self):
        """Doubling prose length roughly doubles decode time, not quadruples it."""
        halved = encode_message(self.PROSE[:2_500])
        doubled = encode_message(self.PROSE[:5_000])

        start = time.perf_counter()
        decode_message(halved)
        small = time.perf_counter() - start

        start = time.perf_counter()
        decode_message(doubled)
        large = time.perf_counter() - start

        # Early emission should keep this near 2x. Past 6x means the collapse
        # optimisation has stopped firing and we have regressed to quadratic.
        self.assertLess(large / max(small, 1e-9), 6.0)

    def test_sustained_ambiguity_stays_within_the_api_cap(self):
        """The pathological no-collapse case still fits inside the API budget."""
        encoded = encode_message("Pack my box with five dozen liquor jugs. " * 97)
        self.assertLessEqual(len(encoded.split()), 4_000)
        start = time.perf_counter()
        result = decode_message(encoded)
        elapsed = time.perf_counter() - start
        self.assertIsInstance(result, str)
        self.assertLess(elapsed, 8.0)


class TestCompatibilityShim(unittest.TestCase):
    """The root-level cipher.py shim still exposes the historical names."""

    def test_shim_reexports_the_full_historical_surface(self):
        """Every name the old cipher.py exposed is still importable from cipher."""
        import cipher

        for name in (
            "encode_message",
            "decode_message",
            "decode_flexible_error_reporting",
            "regions",
            "region_names",
            "num_regions",
            "name_to_mappings",
            "ASCII_MIN",
            "ASCII_MAX",
            "REGION_SIZE",
            "MAX_DECODE_BRANCHES",
        ):
            with self.subTest(name=name):
                self.assertTrue(hasattr(cipher, name))

    def test_shim_names_alias_the_package_objects(self):
        """The shim re-exports the same objects, not copies."""
        import cipher

        self.assertIs(cipher.encode_message, encode_message)
        self.assertIs(cipher.decode_message, decode_message)
        self.assertIs(cipher.name_to_mappings, NAME_INDEX)
        self.assertIs(cipher.regions, REGIONS)
        self.assertEqual(cipher.region_names, ["Kanto", "Johto", "Hoenn"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
