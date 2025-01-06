from typing import AsyncContextManager, Callable, Optional
import unittest

from bitarray import bitarray

from spi_element_base import SpiElementBase, SingleTransferOperationRequest
from spi_operation import SingleTransferOperation
from spi_elements.async_return import AsyncReturn


class DemoAdcNop(SingleTransferOperation):
    def __init__(self):
        super().__init__(bitarray("00010001"), None, False)
        return


class DemoAdcReadChannelOp(SingleTransferOperation):
    def __init__(self, id: int):
        if id == 0:
            super().__init__(bitarray("00000000"))
        elif id == 1:
            super().__init__(bitarray("00000001"))
        else:
            raise ValueError("id must be 0 or 1")


class DemoAdc(SpiElementBase):
    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        return SingleTransferOperationRequest(
            operation=DemoAdcNop(),
            callback=None,
        )

    def readChannel(
        self, id: int, callback: Optional[Callable[..., None]] = None
    ) -> AsyncReturn:
        ar = AsyncReturn(callback)
        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                DemoAdcReadChannelOp(0),
                callback=ar.get_callback(),
            ),
        )

        return ar


class TestSpiElementBase(unittest.TestCase):
    def test_init(self):
        pass
