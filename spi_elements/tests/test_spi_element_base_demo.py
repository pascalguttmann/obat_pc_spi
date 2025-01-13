from typing import List, Callable, Optional, Any
import unittest

from bitarray import bitarray
from itertools import accumulate

from util import reverse_string
from spi_element_base import SpiElementBase
from spi_operation import SingleTransferOperation
from spi_elements.async_return import AsyncReturn
from spi_elements.spi_operation_request_iterator import (
    SpiOperationRequestIteratorBase,
    SingleTransferOperationRequest,
)


class DemoAdcNop(SingleTransferOperation):
    def __init__(self):
        super().__init__(bitarray(reverse_string("00010001")), None, False)
        return


class DemoAdcReadChannelOp(SingleTransferOperation):
    def __init__(self, id: int):
        if id == 0:
            super().__init__(bitarray(reverse_string("00000000")))
        elif id == 1:
            super().__init__(bitarray(reverse_string("00000001")))
        else:
            raise ValueError("id must be 0 or 1")


class AggregationOperation(SingleTransferOperation):
    def __init__(self, ops: List[SingleTransferOperation]) -> None:
        self._ops = ops
        cmd = sum([op.get_command() for op in ops], bitarray())
        super().__init__(cmd)

    def _parse_response(self, rsp: bitarray) -> Any:
        bitlens = [op.get_bitlength() for op in self._ops]
        offsets = list(accumulate(bitlens, initial=0))
        return (
            rsp[offset : offset + bitlen] for offset, bitlen in zip(offsets, bitlens)
        )


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


class AdcChain(SpiOperationRequestIteratorBase):
    def __init__(self, adc0: DemoAdc, adc1: DemoAdc):
        self._adc0 = adc0
        self._adc1 = adc1
        super().__init__()

    def __next__(self) -> SingleTransferOperationRequest:
        return self._get_default_operation_request()

    def _get_default_operation_request(self) -> SingleTransferOperationRequest:

        adc0_op_req = next(self._adc0)
        adc1_op_req = next(self._adc1)

        def process_sub_operations(*args) -> None:
            for sub_op_req, response in zip([adc0_op_req, adc1_op_req], args):
                if sub_op_req.operation.get_response_required():
                    sub_op_req.operation.set_response(response)
                if sub_op_req.callback:
                    sub_op_req.callback(sub_op_req.operation.get_parsed_response())
            return None

        aggregated_operation_request = SingleTransferOperationRequest(
            operation=AggregationOperation(
                [
                    adc0_op_req.operation,
                    adc1_op_req.operation,
                ]
            ),
            callback=process_sub_operations,
        )

        return aggregated_operation_request

    def read_all_adcs(
        self, id: int, callback: Optional[Callable[..., None]] = None
    ) -> AsyncReturn:

        ar = AsyncReturn(callback)

        def set_async_return_after_last_sub_operation(*args) -> None:
            _ = args
            if aret_0.is_finished() and aret_1.is_finished():
                adc0_res = aret_0.get_result()
                adc1_res = aret_1.get_result()
                aggregated_operation_callback = ar.get_callback()
                aggregated_operation_callback(adc0_res, adc1_res)

        aret_0 = self._adc0.read_channel(id, set_async_return_after_last_sub_operation)
        aret_1 = self._adc1.read_channel(id, set_async_return_after_last_sub_operation)

        return ar


class TestSpiElementBase(unittest.TestCase):
    def setup(self):
        self.adc0 = DemoAdc()
        self.adc1 = DemoAdc()
        self.adc_chain = AdcChain(self.adc0, self.adc1)

    def test_init(self):
        self.setup()
        aggregate_single_transfer_operation_req = self.adc_chain.__next__()
        self.assertEqual(
            aggregate_single_transfer_operation_req.operation.get_command(),
            DemoAdcNop().get_command() + DemoAdcNop().get_command(),
        )

    def test_fill_fifo(self):
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
