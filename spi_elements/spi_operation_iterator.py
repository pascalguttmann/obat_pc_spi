from abc import ABC, abstractmethod

from dataclasses import dataclass
from typing import Callable, Optional, TypeVar

from spi_operation.single_transfer_operation import SingleTransferOperation


@dataclass
class SingleTransferOperationRequest:
    operation: SingleTransferOperation
    callback: Optional[Callable[..., None]] = None


class SpiOperationIteratorBase(ABC):
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


SpiOperationIterator = TypeVar("SpiOperationIterator", bound=SpiOperationIteratorBase)
