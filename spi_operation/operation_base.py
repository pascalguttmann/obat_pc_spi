from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar


class OperationBase(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Initializes the OperationBase object instance.

        Must be implemented by child class.
        """
        pass


Operation = TypeVar("Operation", bound=OperationBase)
