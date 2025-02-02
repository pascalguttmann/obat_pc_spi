from __future__ import annotations

from typing import Optional
import time
import warnings
import serial
import serial.tools.list_ports

from spi_master.spi_master_base import SpiMasterBase


class ArduinoSpi(SpiMasterBase):
    def __init__(self, port: Optional[str] = None) -> None:
        """Creates the ArduinoSpi object as spi master with mode 0 (CPHA = 0, CPOL =
        0) with a fixed clock rate of approx. 1 MHz

        :param port: COM port of the arduino e.g. 'COM3'
        """
        if port is None:
            port = self._discover_arduino_port()
        self._port = port

    def _discover_arduino_port(self) -> str:
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if "Arduino" in p.description
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            warnings.warn(
                f"Multiple Arduinos found - using the first: {arduino_ports[0]}"
            )

        return arduino_ports[0]

    def init(self) -> None:
        """Initializes the spi master"""
        self._comport = serial.Serial(port=self._port, baudrate=115200, timeout=1)
        time.sleep(2.0)  # wait for arduino boot
        return

    def transfer(self, cs: int, buf: bytearray) -> bytearray:
        """Transfer content of 'buf' via SPI bus with chip select 'cs' enabled

        :param cs: id of chip select used for SPI transfer
        :param buf: bytearray containing bytes to be sent
        :return: bytearray containing bytes received
        """
        if cs != 0:
            raise NotImplementedError(
                "Chipselect != 0, not supported at the moment by ArduinoSpi"
            )

        tx = buf.hex().encode("utf-8") + b"\n"
        self._comport.write(tx)
        time.sleep(len(tx) * 8 / 1e6 + 300e-6)
        rx = bytearray.fromhex(self._comport.readline().decode())
        return bytearray(rx)
