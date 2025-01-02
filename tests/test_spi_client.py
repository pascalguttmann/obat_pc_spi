import unittest
import time

from spi_client import SpiClient, SpiChannel
from spi_server import SpiServer
from spi_master.ch341.ch341 import CH341

from spi_elements.spi_element_base import SpiElementBase
from spi_elements.operation import SingleTransferOperation
from bitarray import bitarray


class TestSpiElement(SpiElementBase):
    def _get_default_operation_command(self) -> SingleTransferOperation:
        return SingleTransferOperation(
            bitarray("1111000011001100"), response_required=True
        )


class TestSpiClient(unittest.TestCase):
    def test_spi_client_init(self):
        server = SpiServer(CH341())
        spi_element = TestSpiElement(name="test spi element", spi_element_childs=None)
        spi_channels = [
            SpiChannel(spi_element=spi_element, transfer_interval=0.1, cs=0)
        ]

        client = SpiClient(server, spi_channels)

        client.start_cyclic_spi_channel_transfer()
        time.sleep(1)
        client.stop_cyclic_spi_channel_transfer()
