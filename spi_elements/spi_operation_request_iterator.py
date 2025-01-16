from abc import ABC, abstractmethod

from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

from spi_elements.async_return import AsyncReturn
from spi_operation.single_transfer_operation import SingleTransferOperation
from spi_operation.sequence_transfer_operation import SequenceTransferOperation


@dataclass
class SingleTransferOperationRequest:
    operation: SingleTransferOperation
    callback: Optional[Callable[..., None]] = None


@dataclass
class SequenceTransferOperationRequest:
    operation: SequenceTransferOperation
    callback: Optional[Callable[..., None]] = None


class SpiOperationRequestIteratorBase(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> SingleTransferOperationRequest:
        """Get the next SingleTransferOperationRequest, that should be processed."""

    @abstractmethod
    def _get_default_operation_request(self) -> SingleTransferOperationRequest:
        """Get the default operation request, that should be written to
        the physical SpiElement if no other operation request is available from
        other sources.

        :return: SingleTransferOperationRequest containing the default
        SingleTransferOperation with command in binary format (MSB first) that
        should be run when no other SingleTransferOperation is requested.
        """

    @abstractmethod
    def nop(
        self,
        callback: Optional[Callable[..., None]] = None,
    ) -> AsyncReturn:
        """Perform no operation. Can be used to wait for a cycle to
        synchoronize multiple spi_elements."""


SpiOperationRequestIterator = TypeVar(
    "SpiOperationRequestIterator", bound=SpiOperationRequestIteratorBase
)
