import unittest
from cipher import decode_flexible_error_reporting

class TestSecurityFix(unittest.TestCase):
    def test_long_char_tag(self):
        # 11 digits, should be rejected by our 10-digit limit
        long_payload = "[CHAR:" + "1" * 11 + "]"
        result = decode_flexible_error_reporting(long_payload)
        self.assertEqual(result, "<?>")

    def test_very_long_char_tag_dos(self):
        # 1 million digits, should be rejected quickly
        long_payload = "[CHAR:" + "1" * 1000000 + "]"
        result = decode_flexible_error_reporting(long_payload)
        self.assertEqual(result, "<?>")

    def test_non_numeric_char_tag(self):
        result = decode_flexible_error_reporting("[CHAR:abc]")
        self.assertEqual(result, "<?>")

    def test_out_of_range_char_tag(self):
        # Unicode max is 0x10FFFF (1114111)
        result = decode_flexible_error_reporting("[CHAR:2000000]")
        self.assertEqual(result, "<?>")

    def test_valid_char_tag(self):
        result = decode_flexible_error_reporting("[CHAR:65]")
        self.assertEqual(result, "A")

    def test_empty_char_tag(self):
        result = decode_flexible_error_reporting("[CHAR:]")
        self.assertEqual(result, "<?>")

if __name__ == "__main__":
    unittest.main()
