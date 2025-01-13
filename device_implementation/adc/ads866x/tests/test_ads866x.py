import unittest

from device_implementation.adc.ads866x import (
    Ads866x,
    Ads866xInputRange,
    WriteHword,
    ReadHword,
    Nop,
    ReadVoltage,
)
from spi_elements.spi_operation_request_iterator import SingleTransferOperationRequest


class TestAds866x(unittest.TestCase):
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
