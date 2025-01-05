from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional, List, TypeVar
from dataclasses import dataclass

from queue import Queue, Empty

from spi_operation.single_transfer_operation import SingleTransferOperation


@dataclass
class SingleTransferOperationRequest:
    operation: SingleTransferOperation
    callback: Optional[Callable[[], None]] = None


class SpiElementBase(ABC):
    def __init__(
        self,
        name: Optional[str],
        spi_element_childs: Optional[List[SpiElementBase]],
        *args,
        **kwargs,
    ) -> None:
        """Initialize the SPI bus master object"""
        _, _ = args, kwargs
        self._set_spi_element_childs(spi_element_childs)
        self._operation_request = Queue()
        self._set_name(name)

    def _set_spi_element_childs(
        self, spi_element_childs: Optional[List[SpiElementBase]]
    ) -> None:
        self._spi_element_childs = spi_element_childs

    def _set_name(self, name: Optional[str]) -> None:
        if name and not self._name_in_sub_elements(name):
            self._name = name
        else:
            raise ValueError(
                f"Name {name} of SpiElement is not unique among child SpiElement."
            )

    def _name_in_sub_elements(self, name: str) -> bool:
        if not self._spi_element_childs:
            return False
        else:
            return any(
                name == sub._name or sub._name_in_sub_elements(name)
                for sub in self._spi_element_childs
            )

    def get_spi_element_by_name(self, name: str) -> SpiElementBase:
        if name == self._name:
            return self
        else:
            if self._spi_element_childs:
                for sub in self._spi_element_childs:
                    try:
                        return sub.get_spi_element_by_name(name)
                    except ValueError:
                        continue

        raise ValueError(f"Name: '{name}' not found for SpiElement: {self}")

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
