import unittest
from bitarray import bitarray
from typing import Callable, cast, List, Optional

from spi_operation import SingleTransferOperation
from spi_element_base import SpiElementBase, SingleTransferOperationRequest
from spi_elements.async_return import AsyncReturn

from aggregate_operation_request_iterator import AggregateOperationRequestIterator


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
    def __init__(self) -> None:
        super().__init__()

    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        return SingleTransferOperationRequest(
            operation=DemoAdcNop(),
            callback=None,
        )

    def read_channel(
        self, id: int, callback: Optional[Callable[..., None]] = None
    ) -> AsyncReturn:
        ar = AsyncReturn(callback)
        self._put_unprocessed_operation_request(
            SingleTransferOperationRequest(
                DemoAdcReadChannelOp(id),
                callback=ar.get_callback(),
            ),
        )

        return ar


class AdcChain(AggregateOperationRequestIterator):
    def __init__(self, adcs: List[DemoAdc]):
        super().__init__(adcs)

    def read_first_adc(
        self, id: int, callback: Optional[Callable[..., None]] = None
    ) -> AsyncReturn:
        return cast(DemoAdc, self._operation_request_iterators[0]).read_channel(id)

    def read_all_adcs(
        self, id: int, callback: Optional[Callable[..., None]] = None
    ) -> AsyncReturn:

        ar = AsyncReturn(callback)

        def set_async_return_after_last_sub_operation(*args) -> None:
            _ = args
            if all([ar.is_finished() for ar in async_returns]):
                async_return_results = [ar.get_result() for ar in async_returns]
                aggregated_operation_callback = ar.get_callback()
                aggregated_operation_callback(*async_return_results)

        async_returns = [
            cast(DemoAdc, op_req_it).read_channel(
                id, set_async_return_after_last_sub_operation
            )
            for op_req_it in self._operation_request_iterators
        ]

        return ar


class TestAggregateOperationRequestIterator(unittest.TestCase):
    def setup(self):
        self.adc0 = DemoAdc()
        self.adc1 = DemoAdc()
        self.adc_chain = AdcChain([self.adc0, self.adc1])

    def test_init(self):
        self.setup()
        aggregate_single_transfer_operation_req = self.adc_chain.__next__()
        self.assertEqual(
            aggregate_single_transfer_operation_req.operation.get_command(),
            DemoAdcNop().get_command() + DemoAdcNop().get_command(),
        )

    def test_fill_fifo_001(self):
        self.setup()
        ar = self.adc_chain.read_all_adcs(0)
        self.assertIsInstance(ar, AsyncReturn)
        self.assertFalse(ar.is_finished())
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc1.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcNop())
        self.assertEqual(self.adc1.__next__().operation, DemoAdcNop())
        self.assertEqual(self.adc0.__next__().operation, DemoAdcNop())
        self.assertEqual(self.adc1.__next__().operation, DemoAdcNop())
        ar = self.adc_chain.read_all_adcs(0)
        ar = self.adc_chain.read_all_adcs(1)
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc1.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(1))
        self.assertEqual(self.adc1.__next__().operation, DemoAdcReadChannelOp(1))

    def test_fill_fifo_002(self):
        self.setup()
        ar = self.adc_chain.read_first_adc(1)
        ar = self.adc_chain.read_first_adc(1)
        ar = self.adc_chain.read_first_adc(1)
        ar = self.adc_chain.read_all_adcs(0)
        self.assertIsInstance(ar, AsyncReturn)
        self.assertFalse(ar.is_finished())
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(1))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(1))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(1))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc1.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcNop())
        self.assertEqual(self.adc1.__next__().operation, DemoAdcNop())
        self.assertEqual(self.adc0.__next__().operation, DemoAdcNop())
        self.assertEqual(self.adc1.__next__().operation, DemoAdcNop())
        ar = self.adc_chain.read_all_adcs(0)
        ar = self.adc_chain.read_all_adcs(1)
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc1.__next__().operation, DemoAdcReadChannelOp(0))
        self.assertEqual(self.adc0.__next__().operation, DemoAdcReadChannelOp(1))
        self.assertEqual(self.adc1.__next__().operation, DemoAdcReadChannelOp(1))
