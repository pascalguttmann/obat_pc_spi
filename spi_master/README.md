# Spi Master

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Obat Software Project for the Programmable Controller (PC) to access SPI peripherals.

Supported USB-to-SPI bridges:

- [x] [arduino_usb_spi_bridge]
- [x] CH341
- [ ] MCP2210
- [ ] FT232X

[arduino_usb_spi_bridge]: https://github.com/pascalguttmann/arduino_usb_spi_bridge

# Installation

## arduino_usb_spi_bridge

Install the software from [arduino_usb_spi_bridge] to your arduino uno as
described in the readme of its documentation. No specialized drivers are
required as the arduino_usb_spi_bridge utilizes a "COM" port for serial data
communication over USB.

## CH341
>
> [!NOTE]
> To install shared libraries and driver modules administrator privileges are required.
> Please note, that the libraries will run with elevated privileges on your device.

### Windows

1. Install the driver `CH341PAR` using `driver/CH341PAR.EXE` (or install
   manually form `driver/CH341PAR.ZIP`)
2. Copy `CH341DLLA64.DLL` (or `CH341DLL.DLL`) to directory
   `C:\Windows\System32\`. The dynamic link libraries are found in
   `driver/CH341PAR.ZIP/CH341PAR/`
3. Connect the CH341 chip if not already connected.
4. You can test the installation by running the python demo script from the
   root of this repository by running the following command. The first
   positional argument specifies the transmitted data as a hexstring. MSByte and
   MSBit transmitted first.

   ```bash
   $ python3 ch341_demo.py BADC0DED
   TX: 0xbadc0ded
   RX: 0xffffffff # received may vary depending on MISO connection
   ```

### Lubuntu (24.04 LTS "noble")

1. Install Linux driver
[./driver/CH341PAR_LINUX.ZIP](./driver/CH341PAR_LINUX.ZIP) and dynamic library

    ```bash
    cd ~/Documents/obat/docs/design/pc/driver/
    sudo apt install make gcc-13
    unzip CH341PAR_LINUX.ZIP
    cd CH341PAR_LINUX/driver
    sudo make install
    ls -Fahl /dev | grep ch34 # this should display an entry "ch34x_pis*"
    cd ../lib/x64/dynamic
    sudo cp libch347.so /usr/lib
    ```

2. Connect the CH341 chip if not already connected.
3. You can test the installation by running the python demo script from the
   root of this repository by running the following command. The first
   positional argument specifies the transmitted data as a hexstring. MSByte and
   MSBit transmitted first.

   ```bash
   $ sudo python3 ch341_demo.py BADC0DED
   TX: 0xbadc0ded
   RX: 0xffffffff # received may vary depending on MISO connection

> [!NOTE]
> `Sudo` is required to access the kernel device (e.g. `/dev/ch34x_pis1`). To
> avoid running the entire process with elevated privileges you can set the
> owner and group of the device used for communication to your user: `sudo
> chown obat:obat /dev/ch34x_pis1`

# SPI Parameters

## arduino_usb_spi_bridge

The arduino_usb_spi_bridge uses a specialized version of
[arduino_usb_spi_bridge] with reduced clock rate of $100kHz$. The SPI
configuration is hardcoded, but can be adapted relatively easy in the code of
[arduino_usb_spi_bridge].

## CH341

SPI Mode and configuration is hardcoded for the CH341. The chip only supports
SPI mode 0 with hardware support. The clock rate is approximately 1.6 MHz
(every fourth bit is stretched for approx 500ns). The chip select stays low for
the transfer of the data passed to a single call to `CH341.transfer()`. The
chip select is low for approximately 3ms with the linux driver and 1ms with the
windows driver.
