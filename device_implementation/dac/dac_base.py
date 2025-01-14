from abc import abstractmethod
from typing import Tuple, Optional, Callable
from spi_elements import SpiElementBase
from spi_elements.async_return import AsyncReturn


class DacBase(SpiElementBase):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def initialize(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Dac device must implement the behavior to initialize the hardware
        and enable subsequent calls to other methods of the dac."""

    @abstractmethod
    def write(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Write the quantizied analog voltage(s)."""
