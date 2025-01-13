import unittest
import time

from bitarray import bitarray
from typing import Any

from util import reverse_string
from spi_client_server.spi_client import SpiClient, SpiChannel
from spi_client_server.spi_server import SpiServer
from spi_master.virtual.virtual import Virtual
from spi_elements.spi_element_base import SpiElementBase, SingleTransferOperationRequest
from spi_operation import SingleTransferOperation


class TestSingleTransferOperation(SingleTransferOperation):
    def __init__(self) -> None:
        super().__init__(
            bitarray(reverse_string("1111000011001100")), response_required=True
        )
        return None

    def _parse_response(self, rsp: bitarray) -> Any:
        _ = rsp
        return 42


class TestSpiElement(SpiElementBase):
    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        return SingleTransferOperationRequest(
            operation=TestSingleTransferOperation(),
            callback=myCallback,
        )


def myCallback(*args) -> None:
    if not args[0] == 42:
        raise ValueError
    return None


class TestSpiClient(unittest.TestCase):
    def test_spi_client_init(self):
        server = SpiServer(Virtual())
        spi_element = TestSpiElement()
        spi_channels = [SpiChannel(spi_element, transfer_interval=0.1, cs=0)]

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
