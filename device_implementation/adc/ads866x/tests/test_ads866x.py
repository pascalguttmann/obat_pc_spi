import unittest

from bitarray import bitarray

from device_implementation.adc.ads866x import (
    Ads866x,
    Ads866xInputRange,
    WriteHword,
    ReadHword,
    Nop,
    ReadVoltage,
)
from device_implementation.adc.ads866x import Ads866xSingleTransferOperation
from device_implementation.adc.ads866x.registers import DeviceIdReg


class TestAds866x(unittest.TestCase):
    def test_ads866x_single_transfer_operation(self):
        st_op = Ads866xSingleTransferOperation(
            op=bitarray("10000"),
            byte_selector=bitarray("00"),
            addr=bitarray("010101010"),
            data=bitarray("00000000 00000000"),
        )
        self.assertEqual(
            st_op.get_command(), bitarray("0000000000000000 010101010 00 10000")
        )

    def test_register_data_modified(self):
        reg = DeviceIdReg()
        reg.data[reg.DEVICE_ADDR.slice] = bitarray("1010")
        self.assertEqual(reg.data[16], 1)
        self.assertEqual(reg.data[17], 0)
        self.assertEqual(reg.data[18], 1)
        self.assertEqual(reg.data[19], 0)

    def test_init(self):
        _ = Ads866x()

    def test_initialize(self):
        adc = Ads866x()
        adc.initialize(callback=None, input_range=Ads866xInputRange.BIPOLAR_2V56)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, Nop)
        self.assertIsInstance(next(adc).operation, Nop)

    def test_read(self):
        adc = Ads866x()
        adc.initialize(callback=None, input_range=Ads866xInputRange.BIPOLAR_2V56)
        adc.read(callback=None)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, WriteHword)
        self.assertIsInstance(next(adc).operation, ReadHword)
        self.assertIsInstance(next(adc).operation, ReadHword)

        self.assertIsInstance(next(adc).operation, ReadVoltage)
        self.assertIsInstance(next(adc).operation, Nop)
        adc.read(callback=None)
        self.assertIsInstance(next(adc).operation, ReadVoltage)
        self.assertIsInstance(next(adc).operation, Nop)
