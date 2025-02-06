if __name__ == "__main__":
    from spi_master.arduino_spi import ArduinoSpi as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.pss import Pss

    device = Pss()

    client = SpiClient(
        spi_server=SpiServer(SpiMaster()),
        spi_channels=[
            SpiChannel(
                spi_operation_request_iterator=device,
                transfer_interval=100e-3,
                cs=0,
                pre_transfer_channel_initialization=device.get_pre_transfer_initialization(),
            )
        ],
    )

    client.start_cyclic_spi_channel_transfer()
    print("cyclic spi channel transfer started")

    device.initialize().wait()

    device.get_conf_dac().write(callback=None, addr=0, voltage=5.0 * 0xFFF / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=1, voltage=5.0 * 0xFFF / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=2, voltage=5.0 * 0x800 / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=3, voltage=5.0 * 0x800 / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=4, voltage=5.0 * 0x100 / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=5, voltage=5.0 * 0xE00 / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=6, voltage=5.0 * 0xE00 / 0xFFF)
    device.get_conf_dac().write(callback=None, addr=7, voltage=5.0 * 0x100 / 0xFFF)

    device.get_conf_dac().load_all_channels(callback=None).wait()
    print("dac channels loaded")

    client.stop_cyclic_spi_channel_transfer()

    del client
