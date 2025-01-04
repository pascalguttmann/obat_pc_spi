from __future__ import annotations

from abc import ABC, abstractmethod
from multiprocessing import Value
from typing import Optional, List, TypeVar

from queue import Queue, Empty, Full

from spi_operation.single_transfer_operation import SingleTransferOperation


class SpiElementBase(ABC):
    def __init__(
        self,
        name: Optional[str],
        spi_element_childs: Optional[List[SpiElementBase]],
        *args,
        **kwargs,
    ) -> None:
        """Initialize the SPI bus master object"""
        self._set_spi_element_childs(spi_element_childs)
        self._operation_unprocessed = Queue()
        self._operation_processed = Queue()
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

    def pop_unprocessed_operation(self) -> SingleTransferOperation:
        """Pop the next operation as an bitarray, that should be written to the
        physical SpiElement from the fifo of unprocessed operations.

        :return: operation containing the operation in binary format (MSB first)
        """
        try:
            return self._operation_unprocessed.get_nowait()
        except Empty:
            return self._get_default_operation_command()

    def put_processed_operation(self, operation: SingleTransferOperation) -> None:
        """Put the operations response as an bitarray, after the physical
        SpiElement responded to the fifo of processed operations.

        :param response: Operation containing the operation response in binary
        format (MSB first)
        """
        return self._operation_processed.put_nowait(operation)

    @abstractmethod
    def _get_default_operation_command(self) -> SingleTransferOperation:
        """Get the default operation as an bitarray, that should be written to
        the physical SpiElement if no operation command is available from the
        fifo

        :return: Operation containing the default operation command in binary format
        (MSB first)
        """


SpiElement = TypeVar("SpiElement", bound=SpiElementBase)
