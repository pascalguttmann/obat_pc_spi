import unittest

from bitarray import bitarray

from util.util_bitarray import uint_to_bitarray, bitarray_to_uint, concat_bitarray


class TestUtilBitarray(unittest.TestCase):
    len8_val9 = bitarray("10010000")
    len4_val12 = bitarray("0011")

    def test_bitarray_slicing(self):
        self.assertEqual(self.len8_val9[0], 1)
        self.assertEqual(self.len8_val9[1], 0)
        self.assertEqual(self.len8_val9[2], 0)
        self.assertEqual(self.len8_val9[3], 1)
        self.assertEqual(self.len8_val9[4], 0)
        self.assertEqual(self.len8_val9[5], 0)
        self.assertEqual(self.len8_val9[6], 0)
        self.assertEqual(self.len8_val9[7], 0)

    def test_uint_to_bitarray(self):
        self.assertEqual(uint_to_bitarray(n=9, bitlen=8), self.len8_val9)
        self.assertEqual(uint_to_bitarray(n=12, bitlen=4), self.len4_val12)

    def test_bitarrar_to_uint(self):
        self.assertEqual(bitarray_to_uint(self.len8_val9), 9)
        self.assertEqual(bitarray_to_uint(self.len4_val12), 12)

    def test_concat_bitarray_001(self):
        self.assertEqual(
            concat_bitarray(self.len4_val12, self.len8_val9), bitarray("001110010000")
        )

    def test_concat_bitarray_002(self):
        self.assertEqual(
            concat_bitarray(self.len8_val9, self.len4_val12), bitarray("100100000011")
        )
