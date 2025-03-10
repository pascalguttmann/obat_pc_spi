if __name__ == "__main__":
    from spi_master.arduino_spi import ArduinoSpi as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.obat import Obat, EnclosurePeltierPolarity

    from time import sleep

    device = Obat()

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
    input("initialized. press enter to continue")

    device.get_enclosure().write_fan(fan_speed_duty_cycle=1).wait()

    input("Press enter to conitue...")
    device.get_enclosure().write_fan(fan_speed_duty_cycle=0.25).wait()

    input("Press enter to conitue...")
    device.get_enclosure().write_fan(fan_speed_duty_cycle=0).wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
