import unittest
# Make sure cipher.py has the final code with corrected lists and the
# 'decode_message' function (aliased as 'decode_flexible_error_reporting').
from cipher import encode_message, decode_message, decode_flexible_error_reporting

class TestPokemonCipher(unittest.TestCase):

    # --- Encoding Tests ---

    def test_encode_empty_string(self):
        """Encoding an empty string returns an empty string."""
        self.assertEqual(encode_message(""), "")

    def test_encode_simple_word_caps(self):
        """Encoding a simple capitalised word produces the expected Pokémon sequence."""
        # T(84→idx52, K0)→Persian, e(101→idx69, K0)→Weepinbell,
        # s(115→idx83, K0)→Doduo,  t(116→idx84, K0)→Dodrio
        self.assertEqual(encode_message("Test"), "Persian Weepinbell Doduo Dodrio")

    def test_encode_simple_word_lower(self):
        """Encoding a lowercase word including a repeated character that cycles regions."""
        # t(116→idx84, K0)→Dodrio, e(101→idx69, K0)→Weepinbell,
        # s(115→idx83, K0)→Doduo,  t(116→idx84, J1)→Vileplume  (second 't')
        self.assertEqual(encode_message("test"), "Dodrio Weepinbell Doduo Vileplume")

    def test_encode_repeats_and_cycle(self):
        """Encoding four repeated characters cycles through all three regions."""
        # A(65→idx33, K0)→Nidoking, A(J1)→Geodude, A(H2)→Shroomish, A(K0)→Nidoking
        self.assertEqual(encode_message("AAAA"), "Nidoking Geodude Shroomish Nidoking")

    def test_encode_hello_world_exact(self):
        """Encoding 'Hello World!' produces the documented reference sequence."""
        expected = "Zubat Weepinbell Ponyta Gyarados Slowbro Bulbasaur Mankey Slowpoke Farfetch'd Medicham Bellsprout Ivysaur"
        self.assertEqual(encode_message("Hello World!"), expected)

    def test_encode_space_and_punct(self):
        """Encoding spaces and punctuation respects index 0 and 1 and region cycling."""
        # space(idx0, K0)→Bulbasaur, !(idx1, K0)→Ivysaur, space(idx0, J1)→Chikorita
        self.assertEqual(encode_message(" ! "), "Bulbasaur Ivysaur Chikorita")

    # --- Decoding Tests ---

    def test_decode_empty_string(self):
        """Decoding an empty string returns an empty string."""
        self.assertEqual(decode_message(""), "")

    def test_decode_simple_word_caps(self):
        """Decoding a simple capitalised word sequence returns the original word."""
        self.assertEqual(decode_message("Persian Weepinbell Doduo Dodrio"), "Test")

    def test_decode_repeats_cycle(self):
        """Multi-state decoder resolves a prior ambiguity using later tokens.

        'AAAA' encodes to Nidoking Geodude Shroomish Nidoking.  Geodude is
        ambiguous between 'A' (Johto) and 'i' (Kanto), but the next token
        Shroomish only matches 'A' in Hoenn — so the decoder retroactively
        resolves position 1 as 'A', yielding the correct 'AAAA'.
        """
        self.assertEqual(decode_message("Nidoking Geodude Shroomish Nidoking"), "AAAA")

    def test_decode_hello_world_ambiguity(self):
        """Decoding 'Hello World!' sequence surfaces the genuine Slowpoke ambiguity.

        Both the 'n' and 'o' branches survive the entire sequence, so the
        decoder correctly reports [n,o] for that position rather than guessing.
        """
        encoded_seq = "Zubat Weepinbell Ponyta Gyarados Slowbro Bulbasaur Mankey Slowpoke Farfetch'd Medicham Bellsprout Ivysaur"
        expected_decoded = "Hello W[n,o]rld!"
        self.assertEqual(decode_message(encoded_seq), expected_decoded)

    def test_decode_state_error_improved(self):
        """Multi-state decoder recovers 'I don't know' fully despite mid-stream ambiguity.

        Slowpoke at position 4 is ambiguous [n,o], forking the decoder into two
        branches.  Seaking at position 9 is only valid in the 'n' branch, so the
        'o' branch dies and the decoder retroactively resolves all positions,
        yielding the exact original plaintext.
        """
        encoded_seq = "Golbat Bulbasaur Bellsprout Slowbro Slowpoke Wartortle Dodrio Chikorita Golem Seaking Slowpoke Grimer"
        self.assertEqual(decode_message(encoded_seq), "I don't know")

    def test_decode_unknown_pokemon(self):
        """A sequence containing an unknown Pokémon name produces an unknown marker."""
        encoded_seq = "Zubat FakeMon Ponyta"
        expected = "H<?unknown: FakeMon>l"
        self.assertEqual(decode_message(encoded_seq), expected)

    def test_decode_backward_compat_alias(self):
        """decode_flexible_error_reporting is a working alias for decode_message."""
        self.assertIs(decode_flexible_error_reporting, decode_message)
        result = decode_flexible_error_reporting("Persian Weepinbell Doduo Dodrio")
        self.assertEqual(result, "Test")

    # --- Round-trip Tests ---

    def test_roundtrip_simple(self):
        """Round-tripping a simple string with no known ambiguities returns the original."""
        original = "this may be ok."
        encoded = encode_message(original)
        decoded = decode_message(encoded)
        self.assertEqual(decoded, original)

    def test_roundtrip_hello_world(self):
        """Round-tripping 'Hello World!' exposes the documented Slowpoke ambiguity."""
        original = "Hello World!"
        encoded = encode_message(original)
        decoded = decode_message(encoded)
        expected_final = "Hello W[n,o]rld!"
        self.assertEqual(decoded, expected_final)


# Running the tests from the command line: python -m unittest test_cipher.py
if __name__ == '__main__':
    unittest.main(verbosity=2)