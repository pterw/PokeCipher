import unittest
# eake sure cipher.py has the final code with corrected lists and the
# 'decode_flexible_error_reporting' function.
from cipher import encode_message, decode_flexible_error_reporting

class TestPokemonCipher(unittest.TestCase):

    # --- Encoding Tests ---

    def test_encode_empty_string(self):
        """for testing encoding an empty string."""
        self.assertEqual(encode_message(""), "")

    def test_encode_simple_word_caps(self):
        """for testingencoding a simple capitalized word."""
        # T(84,K0)->Dodrio, e(69,K0)->Weepinbell, s(83,K0)->Doduo, t(84,K0)->Dodrio
        self.assertEqual(encode_message("Test"), "Persian Weepinbell Doduo Dodrio")

    def test_encode_simple_word_lower(self):
        """for testing encoding a simple lowercase word."""
         # t(116,K0)->Dodrio, e(101,K0)->Weepinbell, s(115,K0)->Doduo, t(116,J1)->Gloom
        self.assertEqual(encode_message("test"), "Dodrio Weepinbell Doduo Vileplume")

    def test_encode_repeats_and_cycle(self):
        """for testing encoding repeated characters to verify region cycling."""
        # A(65,K0)->Machop, A(65,J1)->Bellsprout, A(65,H2)->Roselia, A(65,K0)->Machop
        self.assertEqual(encode_message("AAAA"), "Nidoking Geodude Shroomish Nidoking")

    def test_encode_hello_world_exact(self):
        """for testing 'Hello World!' accurately."""
        # Expected sequence based on final corrected lists and logic
        expected = "Zubat Weepinbell Ponyta Gyarados Slowbro Bulbasaur Mankey Slowpoke Farfetch'd Medicham Bellsprout Ivysaur"
        # use input without trailing newline for direct function test
        self.assertEqual(encode_message("Hello World!"), expected)

    def test_encode_space_and_punct(self):
        """for testing spaces and punctuation."""
        # space(0,K0)->Bulbasaur, !(1,K0)->Ivysaur, Space(0,J1)->Chikorita
        self.assertEqual(encode_message(" ! "), "Bulbasaur Ivysaur Chikorita")

    # --- decoding tests ---

    def test_decode_empty_string(self):
        """for testing an empty string."""
        self.assertEqual(decode_flexible_error_reporting(""), "")

    def test_decode_simple_word_caps(self):
        """for testing decoding a simple capitalized word sequence."""
        self.assertEqual(decode_flexible_error_reporting("Persian Weepinbell Doduo Dodrio"), "Test")

    def test_decode_repeats_cycle(self):
        """for testing decoding repeats past the three regions to loop back to start region"""
        self.assertEqual(decode_flexible_error_reporting("Nidoking Geodude Shroomish Nidoking"), "A[A,i][A][A]")

    def test_decode_hello_world_ambiguity(self):
        """for testing decoding 'Hello World!' sequence, expecting ambiguity marker."""
        encoded_seq = "Zubat Weepinbell Ponyta Gyarados Slowbro Bulbasaur Mankey Slowpoke Farfetch'd Medicham Bellsprout Ivysaur"
        # expect ambiguity marker '[n,o]' for Slowpoke
        expected_decoded = "Hello W[n,o]rld!"
        self.assertEqual(decode_flexible_error_reporting(encoded_seq), expected_decoded)

    def test_decode_state_error_display(self):
        """for testing decoding a sequence known to cause state errors."""
        # sequence for "I don't know"
        encoded_seq = "Golbat Bulbasaur Bellsprout Slowbro Slowpoke Wartortle Dodrio Chikorita Golem Seaking Slowpoke Grimer"
        # state error on Seaking (shows all its possible chars 'R','n')
        # expect ambiguity on Slowpoke ('n','o')
        expected_decoded = "I do[n,o]'t k[R,n][n,o]w"
        self.assertEqual(decode_flexible_error_reporting(encoded_seq), expected_decoded)

    def test_decode_unknown_pokemon(self):
        """for testing a sequence with a unknown/fake/madeup pokemon."""
        encoded_seq = "Zubat FakeMon Ponyta"
        expected = "H<?unknown: FakeMon>l"
        self.assertEqual(decode_flexible_error_reporting(encoded_seq), expected)

    # --- round-trip tests ---

    def test_roundtrip_simple(self):
        """test encoding then decoding a simple string."""
        original = "this may be ok."
        encoded = encode_message(original)
        decoded = decode_flexible_error_reporting(encoded)
        # for simple text without known issues, it should likely match
        # might need adjustment if ambiguities ARE expected
        self.assertEqual(decoded, original)

    def test_roundtrip_hello_world(self):
        """for testing roundtrip for Hello World expecting ambiguity."""
        original = "Hello World!"
        encoded = encode_message(original)
        decoded = decode_flexible_error_reporting(encoded)
        expected_final = "Hello W[n,o]rld!"
        self.assertEqual(decoded, expected_final)


# running the tests from the command line: python -m unittest test_cipher.py
if __name__ == '__main__':
    unittest.main(verbosity=2) # verbosity=2 gives more output details