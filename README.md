# obat-pc-spi-driver

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Obat Software Project for the Programmable Controller (PC) to access SPI peripherals.

For information about the usb to spi converters called [`spi_master`] in the
software please refer to: [`./spi_master/README.md`][./spi_master/README.md].

[`spi_master`]: ./spi_master/README.md

## Typical Usecases

To run this software on your system you must have the required python packages
installed. To install them (only in the virtual environment, not globally) you
can use the script `go_venv.sh`.

```bash
source go_venv.sh
```

Additionally, for the import system the python path must be updated. For this
you can use the script `export_pythonpath.sh`.

```bash
source export_pythonpath.sh
```

After this setup you are ready to proceed with the desired use case.

### Run Unittest

To run the unittests of this software use:

```bash
python3 -m unittest
```

### Debugging Spi Devices

You want to manually send data via spi to a device? There are multiple ways to
do this using different amounts of this software.

#### Directly sending via the `spi_master`

Sending data directly using the [`spi_master`] will use the least amount of this
software and is a good choice if you are trying to detect if a bug is in
software of hardware. The [`spi_master`] you are using shall supply a demo script
which you can use to send data. For the `arduino_usb_spi_bridge` to start the
demo script you would use the following:

```bash
python3 spi_master/arduino_spi/arduino_spi_demo.py
```

#### Using the spi client server implementation

If the [`spi_master`] you are using does not supply a demo script or you simply
want to use a unified interface when working with different [`spi_master`]s you
can use the demonstration script of the client server implementation. This
typically is the most convenient and also utilizes the setup of the client
sending the data to a server, which in turn communicates on your behalf with
the [`spi_master`].

In the file `./spi_client_server/spi_client_manual_demo.py` you can change the
used [`spi_master`] to the one you want to use. For example to use the
`arduino_usb_spi_bridge` the relevant code looks like this:

```python
    from spi_master.arduino_spi.arduino_spi import ArduinoSpi
    ...
    with SpiServer(ArduinoSpi()) as spi_server:
    ...
```

With this setup you can execute the demo script by running:

```bash
python3 spi_client_server/spi_client_manual_demo.py
```
