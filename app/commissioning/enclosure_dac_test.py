if __name__ == "__main__":
    from spi_master.arduino_spi import ArduinoSpi as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.enclosure import Enclosure, EnclosurePeltierPolarity

    from time import sleep

    device = Enclosure()

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
    input(
        "Enclosure initialized. Press enter to continue...\n"
        + "WARNING: This will write all DAC channels to 4V, make sure no loads are connected at the outputs."
    )

    for addr in range(8):
        device.get_dac().write(addr=addr, voltage=4.0)
    device.get_dac().load_all_channels().wait()

    for addr in range(8):
        device.get_dac().write(addr=addr, voltage=4.0)
    input(
        "Channels written. Press enter to continue...\n"
        + "WARNING: This will write all DAC channels to 0V, make sure no loads are connected at the outputs."
    )
    device.get_dac().load_all_channels().wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
