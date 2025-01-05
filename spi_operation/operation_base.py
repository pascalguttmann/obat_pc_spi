from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar


class OperationBase(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initializes the OperationBase object instance.

        Must be implemented by child class.
        """

    @abstractmethod
    def __repr__(self) -> str:
        """Return a str to represent the object instance for printing.

        Must be implemented by child class.
        """

    @abstractmethod
    def __len__(self) -> int:
        """Returns the number of spi transfers required to process this operation."""

    @abstractmethod
    def __eq__(self, other: object, /) -> bool:
        """Checks if the two operations are equal."""

Operation = TypeVar("Operation", bound=OperationBase)
