# obat-pc-spi-driver

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Obat Software Project for the Programmable Controller (PC) to access SPI peripherals

# Installation

> [!note] "Administrator Privileges"
> To install shared libraries and driver modules administrator privileges are required.
> Please note, that the libraries will run with elevated privileges on your device.

## Windows

1. Install the driver `CH341PAR` using `driver/CH341PAR.EXE` (or install
   manually form `driver/CH341PAR.ZIP`)
2. Copy `CH341DLLA64.DLL` (or `CH341DLL.DLL`) to directory
   `C:\Windows\System32\`. The dynamic link libraries are found in
   `driver/CH341PAR.ZIP/CH341PAR/`
