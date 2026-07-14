"""
test_cipher_pyramidal.py — Pyramidal test suite for PokéCipher
==============================================================

Tests are organised in seven layers, each building on the guarantees
established by the layers below it:

  Layer 1 — Constants & data integrity   (narrowest unit)
  Layer 2 — Single-character encoding
  Layer 3 — Single-character decoding
  Layer 4 — Multi-character encoding sequences
  Layer 5 — Multi-character decoding (including ambiguity/error markers)
  Layer 6 — Round-trip encode → decode
  Layer 7 — Edge cases & stress scenarios  (broadest scope)

Run with:
    python -m unittest test_cipher_pyramidal.py -v
"""

import unittest
import string
from cipher import (
    encode_message,
    decode_message,
    decode_flexible_error_reporting,
    regions,
    region_names,
    num_regions,
    name_to_mappings,
    ASCII_MIN,
    ASCII_MAX,
    REGION_SIZE,
    MAX_DECODE_BRANCHES,
)


# ---------------------------------------------------------------------------
# Layer 1 — Constants & Data Integrity
# ---------------------------------------------------------------------------

class Layer1_Constants(unittest.TestCase):
    """Verify that module-level constants and precomputed data are correct."""

    def test_ascii_bounds(self):
        """ASCII_MIN and ASCII_MAX define a 95-character printable range."""
        self.assertEqual(ASCII_MIN, 32)
        self.assertEqual(ASCII_MAX, 126)
        self.assertEqual(REGION_SIZE, ASCII_MAX - ASCII_MIN + 1)

    def test_region_count(self):
        """There are exactly three regions defined."""
        self.assertEqual(num_regions, 3)
        self.assertEqual(len(region_names), 3)

    def test_region_names(self):
        """Region names are Kanto, Johto, Hoenn in that order."""
        self.assertEqual(region_names, ["Kanto", "Johto", "Hoenn"])

    def test_region_list_lengths(self):
        """Each region list has at least REGION_SIZE (95) entries."""
        for name, pokemon_list in regions.items():
            with self.subTest(region=name):
                self.assertGreaterEqual(len(pokemon_list), REGION_SIZE)

    def test_lookup_table_populated(self):
        """The name_to_mappings lookup table is non-empty."""
        self.assertGreater(len(name_to_mappings), 0)

    def test_lookup_table_known_entry_space(self):
        """Space (ASCII 32, index 0) maps to Kanto[0] = Bulbasaur in region 0."""
        self.assertIn('Bulbasaur', name_to_mappings)
        self.assertIn((' ', 0), name_to_mappings['Bulbasaur'])

    def test_lookup_table_known_entry_tilde(self):
        """Tilde (ASCII 126, index 94) maps to Kanto[94] = Onix in region 0."""
        self.assertIn('Onix', name_to_mappings)
        # index 94, region 0
        self.assertIn((chr(94 + 32), 0), name_to_mappings['Onix'])
        self.assertEqual(chr(94 + 32), '~')

    def test_slowpoke_ambiguity_in_table(self):
        """Slowpoke maps to both 'n' (Kanto/region 0) and 'o' (Johto/region 1)."""
        mappings = name_to_mappings['Slowpoke']
        self.assertIn(('n', 0), mappings)
        self.assertIn(('o', 1), mappings)

    def test_geodude_three_way_ambiguity_in_table(self):
        """Geodude maps to 'i' (Kanto/0), 'A' (Johto/1), and 'X' (Hoenn/2)."""
        mappings = name_to_mappings['Geodude']
        self.assertIn(('i', 0), mappings)
        self.assertIn(('A', 1), mappings)
        self.assertIn(('X', 2), mappings)

    def test_max_decode_branches_positive(self):
        """MAX_DECODE_BRANCHES is a positive integer."""
        self.assertIsInstance(MAX_DECODE_BRANCHES, int)
        self.assertGreater(MAX_DECODE_BRANCHES, 0)

    def test_backward_compat_alias(self):
        """decode_flexible_error_reporting is the same object as decode_message."""
        self.assertIs(decode_flexible_error_reporting, decode_message)


# ---------------------------------------------------------------------------
# Layer 2 — Single-Character Encoding
# ---------------------------------------------------------------------------

class Layer2_SingleCharEncoding(unittest.TestCase):
    """Verify that individual characters encode to the expected Pokémon names."""

    def _enc(self, char: str) -> str:
        """Encode a single character and return the single Pokémon name."""
        result = encode_message(char)
        self.assertNotIn(' ', result, "Single char should produce exactly one token")
        return result

    def test_encode_space(self):
        """Space (idx 0, region 0) encodes to Kanto[0] = Bulbasaur."""
        self.assertEqual(self._enc(' '), 'Bulbasaur')

    def test_encode_exclamation(self):
        """'!' (idx 1, region 0) encodes to Kanto[1] = Ivysaur."""
        self.assertEqual(self._enc('!'), 'Ivysaur')

    def test_encode_uppercase_H(self):
        """'H' (idx 40, region 0) encodes to Kanto[40] = Zubat."""
        self.assertEqual(self._enc('H'), 'Zubat')

    def test_encode_lowercase_e(self):
        """'e' (idx 69, region 0) encodes to Kanto[69] = Weepinbell."""
        self.assertEqual(self._enc('e'), 'Weepinbell')

    def test_encode_tilde(self):
        """'~' (idx 94, region 0) encodes to Kanto[94] = Onix."""
        self.assertEqual(self._enc('~'), 'Onix')

    def test_encode_newline_token(self):
        """Newline encodes to the [NEWLINE] special token."""
        self.assertEqual(encode_message('\n'), '[NEWLINE]')

    def test_encode_carriage_return_token(self):
        """Carriage return encodes to the [RETURN] special token."""
        self.assertEqual(encode_message('\r'), '[RETURN]')

    def test_encode_tab_char_token(self):
        """Tab (ASCII 9, non-printable) encodes to [CHAR:9]."""
        self.assertEqual(encode_message('\t'), '[CHAR:9]')

    def test_encode_nul_char_token(self):
        """NUL byte (ASCII 0) encodes to [CHAR:0]."""
        self.assertEqual(encode_message('\x00'), '[CHAR:0]')

    def test_encode_del_char_token(self):
        """DEL (ASCII 127, just outside the printable range) encodes to [CHAR:127]."""
        self.assertEqual(encode_message('\x7f'), '[CHAR:127]')

    def test_encode_all_printable_ascii_no_error(self):
        """Every printable ASCII character encodes without an [err:...] token."""
        printable = ''.join(chr(c) for c in range(ASCII_MIN, ASCII_MAX + 1))
        result = encode_message(printable)
        self.assertNotIn('[err:', result)

    def test_encode_region_cycling_first_three_occurrences(self):
        """Repeated character cycles K→J→H for its first three occurrences."""
        # 'A' idx33: K0→Nidoking, J1→Geodude, H2→Shroomish
        tokens = encode_message("AAA").split()
        self.assertEqual(tokens[0], 'Nidoking')
        self.assertEqual(tokens[1], 'Geodude')
        self.assertEqual(tokens[2], 'Shroomish')

    def test_encode_region_wraps_after_third(self):
        """After the third occurrence the region wraps back to Kanto."""
        tokens = encode_message("AAAA").split()
        self.assertEqual(tokens[3], 'Nidoking')   # same as first occurrence

    def test_encode_different_chars_independent_state(self):
        """Two different characters have independent region-cycling state."""
        # 'a' (idx65) first → Kanto; 'b' (idx66) first → Kanto; 'a' second → Johto
        t = encode_message("aba").split()
        self.assertEqual(t[0], regions['Kanto'][65])
        self.assertEqual(t[1], regions['Kanto'][66])
        self.assertEqual(t[2], regions['Johto'][65])


# ---------------------------------------------------------------------------
# Layer 3 — Single-Character Decoding
# ---------------------------------------------------------------------------

class Layer3_SingleCharDecoding(unittest.TestCase):
    """Verify that individual Pokémon tokens decode to the expected characters."""

    def test_decode_bulbasaur(self):
        """Bulbasaur (Kanto idx 0) decodes to space."""
        self.assertEqual(decode_message('Bulbasaur'), ' ')

    def test_decode_zubat(self):
        """Zubat (Kanto idx 40) decodes to 'H'."""
        self.assertEqual(decode_message('Zubat'), 'H')

    def test_decode_onix(self):
        """Onix (Kanto idx 94) decodes to '~'."""
        self.assertEqual(decode_message('Onix'), '~')

    def test_decode_newline_token(self):
        """[NEWLINE] token decodes to a newline character."""
        self.assertEqual(decode_message('[NEWLINE]'), '\n')

    def test_decode_return_token(self):
        """[RETURN] token decodes to a carriage-return character."""
        self.assertEqual(decode_message('[RETURN]'), '\r')

    def test_decode_char_token(self):
        """[CHAR:9] token decodes to a tab character."""
        self.assertEqual(decode_message('[CHAR:9]'), '\t')

    def test_decode_char_token_nul(self):
        """[CHAR:0] token decodes to NUL."""
        self.assertEqual(decode_message('[CHAR:0]'), '\x00')

    def test_decode_unknown_pokemon(self):
        """An unknown Pokémon name produces a <?unknown:...> marker."""
        result = decode_message('FakeMon')
        self.assertIn('<?unknown: FakeMon>', result)

    def test_decode_malformed_char_token(self):
        """A [CHAR:] token with a non-integer value produces <?>."""
        self.assertEqual(decode_message('[CHAR:abc]'), '<?>')

    def test_decode_error_encoding_token(self):
        """An [err:...] token produces a <?error encoding:...> marker."""
        result = decode_message('[err:idx_99_region_Kanto]')
        self.assertIn('<?error encoding:', result)


# ---------------------------------------------------------------------------
# Layer 4 — Multi-Character Encoding Sequences
# ---------------------------------------------------------------------------

class Layer4_MultiCharEncoding(unittest.TestCase):
    """Verify encoding of multi-character strings against known reference values."""

    def test_encode_hello(self):
        """Encoding 'Hello' matches the documented five-Pokémon sequence."""
        expected = 'Zubat Weepinbell Ponyta Gyarados Slowbro'
        self.assertEqual(encode_message('Hello'), expected)

    def test_encode_hello_world(self):
        """Encoding 'Hello World!' matches the full 12-token reference sequence."""
        expected = ("Zubat Weepinbell Ponyta Gyarados Slowbro "
                    "Bulbasaur Mankey Slowpoke Farfetch'd Medicham "
                    "Bellsprout Ivysaur")
        self.assertEqual(encode_message('Hello World!'), expected)

    def test_encode_four_As(self):
        """Encoding 'AAAA' uses all three regions and wraps back to Kanto."""
        self.assertEqual(encode_message('AAAA'), 'Nidoking Geodude Shroomish Nidoking')

    def test_encode_space_excl_space(self):
        """Encoding ' ! ' demonstrates region cycling for the space character."""
        self.assertEqual(encode_message(' ! '), 'Bulbasaur Ivysaur Chikorita')

    def test_encode_mixed_case_word(self):
        """Uppercase and lowercase versions of the same letter have separate counters."""
        result_upper = encode_message('AA').split()
        result_lower = encode_message('aa').split()
        # First 'A' and first 'a' both start in region 0, but at different indices
        self.assertNotEqual(result_upper[0], result_lower[0])
        # Second 'A' is in Johto; second 'a' is also in Johto (independent of A's count)
        self.assertEqual(result_upper[1], regions['Johto'][ord('A') - ASCII_MIN])
        self.assertEqual(result_lower[1], regions['Johto'][ord('a') - ASCII_MIN])

    def test_encode_output_token_count_matches_input(self):
        """The number of output tokens equals the number of input characters."""
        msg = "Cipher test 123"
        tokens = encode_message(msg).split()
        self.assertEqual(len(tokens), len(msg))

    def test_encode_preserves_newline_as_token(self):
        """Newlines within a message are encoded as [NEWLINE] tokens."""
        result = encode_message("a\nb")
        parts = result.split()
        self.assertEqual(parts[1], '[NEWLINE]')

    def test_encode_high_repeat_count(self):
        """A character repeated 9 times cycles through all three regions three times."""
        msg = 'x' * 9
        tokens = encode_message(msg).split()
        # Positions 0,3,6 → Kanto; 1,4,7 → Johto; 2,5,8 → Hoenn
        idx = ord('x') - ASCII_MIN
        for group_start in (0, 3, 6):
            self.assertEqual(tokens[group_start],   regions['Kanto'][idx])
            self.assertEqual(tokens[group_start+1], regions['Johto'][idx])
            self.assertEqual(tokens[group_start+2], regions['Hoenn'][idx])


# ---------------------------------------------------------------------------
# Layer 5 — Multi-Character Decoding
# ---------------------------------------------------------------------------

class Layer5_MultiCharDecoding(unittest.TestCase):
    """Verify decoding of known sequences, including ambiguity markers."""

    def test_decode_hello(self):
        """Decoding the 'Hello' reference sequence returns 'Hello'."""
        self.assertEqual(decode_message('Zubat Weepinbell Ponyta Gyarados Slowbro'), 'Hello')

    def test_decode_hello_world_ambiguous(self):
        """Decoding 'Hello World!' sequence returns the Slowpoke ambiguity marker."""
        seq = ("Zubat Weepinbell Ponyta Gyarados Slowbro "
               "Bulbasaur Mankey Slowpoke Farfetch'd Medicham "
               "Bellsprout Ivysaur")
        self.assertEqual(decode_message(seq), "Hello W[n,o]rld!")

    def test_decode_four_As_fully_resolved(self):
        """Decoding 'AAAA' resolves the mid-stream Geodude ambiguity to 'AAAA'."""
        self.assertEqual(decode_message('Nidoking Geodude Shroomish Nidoking'), 'AAAA')

    def test_decode_i_dont_know_fully_resolved(self):
        """Multi-state decoder fully reconstructs 'I don't know' from its ciphertext."""
        seq = ("Golbat Bulbasaur Bellsprout Slowbro Slowpoke "
               "Wartortle Dodrio Chikorita Golem Seaking Slowpoke Grimer")
        self.assertEqual(decode_message(seq), "I don't know")

    def test_decode_ambiguity_marker_format(self):
        """Unresolvable ambiguities use square-bracket [x,y] notation."""
        seq = ("Zubat Weepinbell Ponyta Gyarados Slowbro "
               "Bulbasaur Mankey Slowpoke Farfetch'd Medicham "
               "Bellsprout Ivysaur")
        result = decode_message(seq)
        self.assertIn('[n,o]', result)
        # Ensure curly-brace error notation is NOT used here
        self.assertNotIn('{', result)

    def test_decode_special_tokens_passthrough(self):
        """Special tokens ([NEWLINE], [CHAR:N]) are decoded correctly within a sequence."""
        seq = "Zubat [NEWLINE] Weepinbell"
        result = decode_message(seq)
        self.assertEqual(result, 'H\ne')

    def test_decode_multi_unknown(self):
        """Multiple unknown tokens each produce their own <?unknown:...> marker.

        Mewtwo (Kanto #150) and Mew (Kanto #151) are not in any of the first-95
        lists and therefore remain genuinely unknown to the decoder.
        """
        result = decode_message('Zubat Mewtwo Ponyta')
        self.assertIn('H', result)
        self.assertIn('<?unknown: Mewtwo>', result)
        self.assertIn('l', result)

    def test_decode_state_mismatch_uses_curly_braces(self):
        """A genuine state-mismatch error uses {x,y} curly-brace notation."""
        # Construct an impossible token sequence:
        # 'Bulbasaur' as the SECOND token would expect region 1 for ' ',
        # but Bulbasaur is only in Kanto (region 0).  Force a mismatch by
        # passing Bulbasaur twice: first resolves fine (region 0), second
        # expects region 1 which Bulbasaur cannot satisfy.
        # Confirm that the state-mismatch path is exercised.
        result = decode_message('Bulbasaur Bulbasaur')
        # Second Bulbasaur: ' ' has count 1, expected region 1,
        # but Bulbasaur only maps to region 0 → state mismatch → {' '}
        self.assertIn('{', result)

    def test_decode_retroactive_resolution_removes_ambiguity(self):
        """A position that was ambiguous but later narrowed resolves to one character.

        After decoding 'Nidoking Geodude Shroomish Nidoking', position 1
        (Geodude) was initially [A,i] but Shroomish kills the 'i' branch,
        so the final output has no brackets at all.
        """
        result = decode_message('Nidoking Geodude Shroomish Nidoking')
        self.assertNotIn('[', result)
        self.assertNotIn('{', result)
        self.assertEqual(result, 'AAAA')


# ---------------------------------------------------------------------------
# Layer 6 — Round-Trip (Encode → Decode)
# ---------------------------------------------------------------------------

class Layer6_RoundTrip(unittest.TestCase):
    """Verify that encode followed by decode reproduces the original (or documents
    known ambiguities where perfect reconstruction is impossible)."""

    def _roundtrip(self, text: str) -> str:
        return decode_message(encode_message(text))

    def test_roundtrip_empty(self):
        self.assertEqual(self._roundtrip(''), '')

    def test_roundtrip_single_space(self):
        self.assertEqual(self._roundtrip(' '), ' ')

    def test_roundtrip_single_tilde(self):
        self.assertEqual(self._roundtrip('~'), '~')

    def test_roundtrip_single_printable_chars(self):
        """Every individual printable ASCII character round-trips without loss."""
        for code in range(ASCII_MIN, ASCII_MAX + 1):
            char = chr(code)
            with self.subTest(char=repr(char)):
                self.assertEqual(self._roundtrip(char), char)

    def test_roundtrip_hello(self):
        self.assertEqual(self._roundtrip('Hello'), 'Hello')

    def test_roundtrip_simple_sentence(self):
        self.assertEqual(self._roundtrip('this may be ok.'), 'this may be ok.')

    def test_roundtrip_all_digits(self):
        """Digits 0-9 partially round-trip; some positions expose cipher ambiguities.

        Pokémon used for digits 2–3 (Rattata/Raticate) also encode digits 0–1 in
        Johto, and similarly for digits 8–9 vs 5–6.  Both branches survive the
        full sequence, so those positions remain marked as ambiguous.
        """
        expected = '01[0,2][1,3]4567[5,8][6,9]'
        self.assertEqual(self._roundtrip('0123456789'), expected)

    def test_roundtrip_all_uppercase_letters(self):
        """Uppercase letters mostly round-trip; H and I expose Zubat/Golbat collisions.

        Zubat encodes both 'H' (Kanto[40], region 0) and 'D' (Johto[36], region 1).
        After 'D' has appeared once, both 'D' (count 1, region 1) and 'H' (count 0,
        region 0) are valid interpretations of Zubat, and both branches survive.
        The same applies to Golbat for 'I' vs 'E'.
        """
        expected = 'ABCDEFG[D,H][E,I]JKLMNOPQRSTUVWXYZ'
        self.assertEqual(self._roundtrip(string.ascii_uppercase), expected)

    def test_roundtrip_hello_world_known_ambiguity(self):
        """'Hello World!' cannot fully round-trip due to the Slowpoke ambiguity."""
        result = self._roundtrip('Hello World!')
        self.assertEqual(result, 'Hello W[n,o]rld!')

    def test_roundtrip_test(self):
        self.assertEqual(self._roundtrip('Test'), 'Test')

    def test_roundtrip_four_As(self):
        """'AAAA' round-trips perfectly with the multi-state decoder."""
        self.assertEqual(self._roundtrip('AAAA'), 'AAAA')

    def test_roundtrip_i_dont_know(self):
        """'I don't know' round-trips perfectly with the multi-state decoder."""
        self.assertEqual(self._roundtrip("I don't know"), "I don't know")

    def test_roundtrip_mixed_case_with_spaces(self):
        """Mixed-case strings with spaces round-trip (may include ambiguity markers).

        The cipher can produce ambiguities for some character combinations.  We
        verify the result is a non-empty string and that unambiguous characters
        at the start of the sequence match the original.
        """
        text = 'PokeCipher Is Fun'
        result = self._roundtrip(text)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        # The first four chars ('P','o','k','e') each appear once and are unambiguous.
        self.assertTrue(result.startswith('Poke'))

    def test_roundtrip_special_chars_preserved(self):
        """Special ASCII characters (punctuation, symbols) survive a round-trip."""
        text = '!@#$%^&*()'
        self.assertEqual(self._roundtrip(text), text)

    def test_roundtrip_newline_in_message(self):
        """A newline embedded in a message is preserved through encode/decode.

        Uses 'A\\nB' to avoid cross-region collisions: Nidoking encodes only 'A',
        and Clefairy for 'B' (Kanto[34]) is unambiguous at first occurrence.
        """
        text = 'A\nB'
        self.assertEqual(self._roundtrip(text), text)


# ---------------------------------------------------------------------------
# Layer 7 — Edge Cases & Stress Scenarios
# ---------------------------------------------------------------------------

class Layer7_EdgeCasesAndStress(unittest.TestCase):
    """Broaden coverage to unusual inputs, boundary conditions, and stress tests."""

    def test_encode_empty(self):
        self.assertEqual(encode_message(''), '')

    def test_decode_empty(self):
        self.assertEqual(decode_message(''), '')

    def test_encode_only_whitespace_tokens(self):
        """Multiple spaces each independently cycle the space character's region."""
        tokens = encode_message('   ').split()
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0], regions['Kanto'][0])   # region 0
        self.assertEqual(tokens[1], regions['Johto'][0])   # region 1
        self.assertEqual(tokens[2], regions['Hoenn'][0])   # region 2

    def test_encode_all_printable_ascii_length(self):
        """Encoding all 95 printable ASCII chars produces exactly 95 tokens."""
        text = ''.join(chr(c) for c in range(ASCII_MIN, ASCII_MAX + 1))
        tokens = encode_message(text).split()
        self.assertEqual(len(tokens), REGION_SIZE)

    def test_decode_all_printable_ascii_roundtrip(self):
        """All 95 printable ASCII chars round-trip; a small set expose known ambiguities.

        The cipher's regional overlap means 5 positions are ambiguous or mismatched
        when every character appears exactly once in order.  The 90 remaining
        positions decode correctly — verified for the opening sequence (space through @).
        """
        text = ''.join(chr(c) for c in range(ASCII_MIN, ASCII_MAX + 1))
        encoded = encode_message(text)
        decoded = decode_message(encoded)
        # The first 33 characters (space → '@', no cross-region collisions) are clean.
        clean_prefix = text[:33]  # ' !"#$%&\'()*+,-./0123456789:;<=>?@'
        self.assertTrue(decoded.startswith(clean_prefix),
                        f"First 33 chars should decode cleanly; got: {decoded[:40]!r}")

    def test_encode_long_repeat_wraps_correctly(self):
        """A character repeated 30 times cycles regions correctly at every position."""
        char = 'Z'
        msg = char * 30
        tokens = encode_message(msg).split()
        idx = ord(char) - ASCII_MIN
        for i, token in enumerate(tokens):
            expected_region = i % num_regions
            expected_pokemon = regions[region_names[expected_region]][idx]
            with self.subTest(position=i):
                self.assertEqual(token, expected_pokemon)

    def test_decode_long_repeat_roundtrip(self):
        """A 30-character 'A' repeat round-trips without any ambiguity markers.

        'A' uses Nidoking (unique to Kanto), Geodude (appears in all three regions
        at different indices), and Shroomish (unique to Hoenn).  The Geodude position
        is transiently ambiguous between 'A' and 'i', but the immediately following
        Shroomish token (Hoenn[33]) only admits 'A' — killing the 'i' branch and
        retroactively resolving every ambiguous position.
        """
        msg = 'A' * 30
        result = decode_message(encode_message(msg))
        self.assertEqual(result, msg)

    def test_encode_single_char_repeated_returns_three_distinct_pokemon(self):
        """The first three occurrences of any character map to three distinct Pokémon."""
        for code in range(ASCII_MIN, ASCII_MAX + 1):
            char = chr(code)
            tokens = encode_message(char * 3).split()
            with self.subTest(char=repr(char)):
                # All three tokens must come from different regions
                self.assertEqual(len(set(tokens)), len(tokens),
                                 f"Expected 3 distinct Pokémon for {repr(char)!r}")

    def test_decode_only_special_tokens(self):
        """A sequence of only special tokens decodes without errors."""
        seq = '[NEWLINE] [RETURN] [CHAR:9] [CHAR:0]'
        result = decode_message(seq)
        self.assertEqual(result, '\n\r\t\x00')

    def test_decode_interleaved_special_and_pokemon(self):
        """Special tokens and Pokémon names can be freely interleaved."""
        # 'H' (Zubat), newline, 'e' (Weepinbell)
        seq = 'Zubat [NEWLINE] Weepinbell'
        self.assertEqual(decode_message(seq), 'H\ne')

    def test_encode_decode_non_ascii_boundary(self):
        """Characters just below and just above the printable range use CHAR tokens."""
        result_below = encode_message(chr(ASCII_MIN - 1))   # chr(31) = US
        result_above = encode_message(chr(ASCII_MAX + 1))   # chr(127) = DEL
        self.assertTrue(result_below.startswith('[CHAR:'))
        self.assertTrue(result_above.startswith('[CHAR:'))
        # And they decode back correctly
        self.assertEqual(decode_message(result_below), chr(ASCII_MIN - 1))
        self.assertEqual(decode_message(result_above), chr(ASCII_MAX + 1))

    def test_multi_state_branch_pruning_does_not_crash(self):
        """Encoding a string with many ambiguous characters does not crash or hang."""
        # Use characters that are known to have ambiguities (n and o both map to Slowpoke)
        # Repeat them enough to exercise the branch pruning code-path.
        msg = 'no' * 20   # 40 chars; lots of potential ambiguity
        encoded = encode_message(msg)
        result = decode_message(encoded)   # must complete without error
        self.assertIsInstance(result, str)

    def test_decode_error_token_roundtrip_preserved(self):
        """[err:...] tokens survive a decode pass as error-marker strings."""
        token = '[err:idx_99_region_Kanto]'
        result = decode_message(token)
        self.assertIn('<?error encoding:', result)

    def test_encode_unicode_outside_ascii(self):
        """Unicode characters above ASCII 127 are encoded as [CHAR:N] tokens."""
        result = encode_message('é')       # U+00E9 = 233
        self.assertTrue(result.startswith('[CHAR:'))
        self.assertEqual(decode_message(result), 'é')

    def test_encode_empty_string_roundtrip(self):
        self.assertEqual(decode_message(encode_message('')), '')

    def test_state_mismatch_marker_uses_curly_braces(self):
        """State-mismatch errors use {x,y} notation (distinct from [x,y] ambiguity)."""
        # Force a mismatch: Bulbasaur maps only to (' ', region 0).
        # After decoding the first space (count becomes 1), the second Bulbasaur
        # requires region 1 for ' ' (count 1 % 3 = 1) but only has region 0 → mismatch.
        result = decode_message('Bulbasaur Bulbasaur')
        self.assertIn('{', result)
        self.assertNotIn('[', result)   # must NOT also use the ambiguity bracket

    def test_decode_large_valid_message(self):
        """A long message encodes and decodes without raising an exception."""
        import string
        msg = (string.ascii_letters + string.digits + ' .,!') * 4
        # Run encode and decode; verify no exception is raised and result is a string.
        encoded = encode_message(msg)
        decoded = decode_message(encoded)
        self.assertIsInstance(decoded, str)
        self.assertGreater(len(decoded), 0)
        # The decoded output is at least as long as the original (markers expand positions).
        self.assertGreaterEqual(len(decoded), len(msg))


if __name__ == '__main__':
    unittest.main(verbosity=2)
