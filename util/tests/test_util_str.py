import unittest

from util.util_str import reverse_string


class TestReverseString(unittest.TestCase):
    def test_reverse_string(self):
        s = "abcd"
        s_reversed = "dcba"
        self.assertEqual(s_reversed, reverse_string(s))

    def test_reverse_string_empty(self):
        s = ""
        s_reversed = ""
        self.assertEqual(s_reversed, reverse_string(s))
