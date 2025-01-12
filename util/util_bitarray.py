from bitarray import bitarray
from functools import reduce
from operator import add
from util import reverse_string


def uint_to_bitarray(n: int, bitlen: int) -> bitarray:
    return bitarray(reverse_string(bin(n)[2:].zfill(bitlen)))


def bitarray_to_uint(ba: bitarray) -> int:
    return int(reverse_string(ba.to01()), 2)


def concat_bitarray(*args: bitarray) -> bitarray:
    """First argument == LSB"""
    for arg in args:
        if not isinstance(arg, bitarray):
            raise ValueError(
                f"Expected argument of type bitarray but got {arg}, which is of type {type(arg)}."
            )

    return reduce(add, args)
