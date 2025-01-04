import unittest
import time

from spi_client import SpiClient, SpiChannel
from spi_server import SpiServer
from spi_master.virtual.virtual import Virtual

from spi_elements.spi_element_base import SpiElementBase
from spi_operation.single_transfer_operation import SingleTransferOperation
from bitarray import bitarray


class TestSpiElement(SpiElementBase):
    def _get_default_operation_command(self) -> SingleTransferOperation:
        return SingleTransferOperation(
            bitarray("1111000011001100"), response_required=True
        )


class TestSpiClient(unittest.TestCase):
    def test_spi_client_init(self):
        server = SpiServer(Virtual())
        spi_element = TestSpiElement(name="test spi element", spi_element_childs=None)
        spi_channels = [
            SpiChannel(spi_element=spi_element, transfer_interval=0.1, cs=0)
        ]

        client = SpiClient(server, spi_channels)
        self.assertFalse(client._spi_channel_threads_run_flag)
        self.assertFalse(client._spi_channel_threads[0].is_alive())
        self.assertTrue(client._spi_channel_threads[0].daemon)

        client.start_cyclic_spi_channel_transfer()
        self.assertTrue(client._spi_channel_threads_run_flag)
        self.assertTrue(client._spi_channel_threads[0].is_alive())
        time.sleep(0.5)

        client.stop_cyclic_spi_channel_transfer()
        self.assertFalse(client._spi_channel_threads_run_flag)
        self.assertFalse(client._spi_channel_threads[0].is_alive())
