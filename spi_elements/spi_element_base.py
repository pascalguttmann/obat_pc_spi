from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional, List, TypeVar
from dataclasses import dataclass

from queue import Queue, Empty

from spi_operation.single_transfer_operation import SingleTransferOperation


@dataclass
class SingleTransferOperationRequest:
    operation: SingleTransferOperation
    callback: Optional[Callable[..., None]] = None


class SpiElementBase(ABC):
    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the SPI bus master object"""
        _, _ = args, kwargs
        self._operation_request = Queue()

    def pop_unprocessed_operation_request(self) -> SingleTransferOperationRequest:
        """Pop the next operation request, that should be written to the
        physical SpiElement from the fifo of unprocessed operations.

        :return: SingleTransferOperationRequest containing the
        SingleTransferOperation with command in binary format (MSB first) that
        shoud be run next.
        """
        try:
            return self._operation_request.get_nowait()
        except Empty:
            return self._get_default_operation_request()

    def _put_unprocessed_operation_request(
        self,
        op_req: SingleTransferOperationRequest | List[SingleTransferOperationRequest],
    ) -> None:
        if not isinstance(op_req, list):
            op_req_list = [op_req]
        else:
            op_req_list = op_req

        for x in op_req_list:
            self._operation_request.put_nowait(x)

    @abstractmethod
    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        """Get the default operation request, that should be written to
        the physical SpiElement if no operation command is available from the
        fifo

        :return: SingleTransferOperationRequest containing the default
        SingleTransferOperation with command in binary format (MSB first) that
        should be run when no other SingleTransferOperation is requested.
        """


SpiElement = TypeVar("SpiElement", bound=SpiElementBase)
