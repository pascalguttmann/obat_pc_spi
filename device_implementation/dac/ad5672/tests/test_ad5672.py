import unittest

from bitarray import bitarray

from device_implementation.dac.ad5672 import Ad5672
from device_implementation.dac.ad5672 import Ad5672SingleTransferOperation


class TestAds866x(unittest.TestCase):
    def test_ads866x_single_transfer_operation(self):
        st_op = Ad5672SingleTransferOperation(
            op=bitarray("1111"),
            addr=bitarray("1010"),
            data=bitarray("0001 00010001"),
            data_fill=bitarray("0000"),
        )
        self.assertEqual(st_op.get_command(), bitarray("0000 000100010001 1010 1111"))
