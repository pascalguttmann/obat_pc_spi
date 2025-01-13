from abc import abstractmethod
from typing import Tuple, Optional, Callable
from spi_elements import SpiElementBase
from spi_elements.async_return import AsyncReturn


class AdcBase(SpiElementBase):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def initialize(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Adc device must implement the behavior to initialize the hardware
        and enable subsequent calls to other methods of the adc."""

    @abstractmethod
    def read(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Read the quantizied analog voltage(s) and return the voltage as float."""
