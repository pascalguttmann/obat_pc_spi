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
    print("initialized.")

    input("Press enter to continue... with 12.5W")
    device.write_heater(heater_power=12.5).wait()

    input("Press enter to continue... with 50.0W")
    device.write_heater(heater_power=50).wait()

    input("Press enter to continue... with 0.0W")
    device.write_heater(heater_power=0).wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
