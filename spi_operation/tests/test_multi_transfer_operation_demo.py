import unittest

from bitarray import bitarray
from typing import List, Tuple, Any

from single_transfer_operation import SingleTransferOperation
from multi_transfer_operation import MultiTransferOperation


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
        command = bitarray(read_opcode + channel_opcode + channel)

        super().__init__(command, response=None, response_required=True)

    def _parse_response(self, rsp: bitarray) -> Any:
        read_success_prefix = bitarray("0001")

        if not read_success_prefix == rsp[0:4]:
            raise RuntimeError("ReadChannel failed on HW.")

        uint4_value = rsp[4:8]
        value: int = int(uint4_value.to01(), base=2)
        return value


# This class is just for demonstration purposes the functionality would be read
# from the datasheet of the spi_element impolementing the operation
# functionality or be defined by the users functional requirements. I.e.
# logical grouping of SingleTransferOperations.
class ReadAllChannels(MultiTransferOperation):
    def __init__(self) -> None:
        operations = [
            ReadChannel(0),
            ReadChannel(1),
        ]
        super().__init__(operations)

    def _parse_response(self, operations_rsp: List[int]) -> Tuple[int, int]:
        val_ch_0 = operations_rsp[0]
        val_ch_1 = operations_rsp[1]

        return (val_ch_0, val_ch_1)


class TestReadAllChannels(unittest.TestCase):
    def test_init(self):
        rc = ReadAllChannels()
        self.assertIsInstance(rc._operations, list)
        self.assertEqual(len(rc._operations), 2)
        for op in rc._operations:
            self.assertIsInstance(op, ReadChannel)

    def test_get_parsed_response_001(self):
        with self.assertRaises(ValueError):
            rc = ReadAllChannels()
            _ = rc.get_parsed_response()

    def test_get_parsed_response_002(self):
        rc = ReadAllChannels()
        rsp = bitarray("0001" + "1101")
        for op in rc.get_single_transfer_operations():
            op.set_response(rsp)
        val = rc.get_parsed_response()
        self.assertEqual(val, (0b1101, 0b1101))
