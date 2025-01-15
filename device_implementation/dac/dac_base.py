from abc import abstractmethod
from typing import Optional, Callable
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
        """Write the quantizied analog voltage to the dac without updating the
        analog output voltage. To update all prior written voltages to the
        output use .load_all_channels()."""

    @abstractmethod
    def load_all_channels(
        self, callback: Optional[Callable[..., None]] = None, *args, **kwargs
    ) -> AsyncReturn:
        """Update all analog output voltages according to the data written
        prior with .write()."""
