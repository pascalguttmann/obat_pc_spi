import unittest

from bitarray import bitarray
from typing import Any

from util import reverse_string, bitarray_to_uint
from single_transfer_operation import SingleTransferOperation


# This class is just for demonstration purposes the functionality would be read
# from the datasheet of the spi_element impolementing the operation
# functionality
class ReadChannel(SingleTransferOperation):
    def __init__(self, channel_id: int) -> None:
        if channel_id != 0 and channel_id != 1:
            raise ValueError("channel_id must be 0 or 1")

        # If more operations use read_opcode this should be abstracted as a
        # parent class e.g. like "ReadRegister"
        read_opcode = "0001"
        channel_opcode = "101"
        channel = bin(channel_id)[2:]
        command = bitarray(reverse_string(read_opcode + channel_opcode + channel))

        super().__init__(command, response=None, response_required=True)

    def _parse_response(self, rsp: bitarray) -> Any:
        read_success_prefix = bitarray(reverse_string("0001"))

        if not read_success_prefix == rsp[4:8]:
            raise RuntimeError("ReadChannel failed on HW.")

        uint4_value = rsp[0:4]
        value: int = bitarray_to_uint(uint4_value)
        return value


class TestReadChannel(unittest.TestCase):
    def test_init(self):
        rc = ReadChannel(0)
        self.assertEqual(rc.get_command(), bitarray(reverse_string("00011010")))
        self.assertEqual(rc.get_response(), None)
        self.assertEqual(rc.get_response_required(), True)

    def test_set_response(self):
        rc = ReadChannel(0)
        rsp = bitarray(reverse_string("00010000"))
        rc.set_response(rsp)
        self.assertEqual(rc.get_response(), rsp)

    def test_get_parsed_response_001(self):
        with self.assertRaises(ValueError):
            rc = ReadChannel(0)
            _ = rc.get_parsed_response()

    def test_get_parsed_response_002(self):
        rc = ReadChannel(0)
        rsp = bitarray(reverse_string("0001" + "1101"))
        rc.set_response(rsp)
        val = rc.get_parsed_response()
        self.assertEqual(val, 0b1101)
