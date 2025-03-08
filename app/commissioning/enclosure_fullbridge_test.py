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

    def enable_fullbridge():
        device.get_dac().write(addr=0, voltage=5.0)
        device.get_dac().write(addr=1, voltage=5.0)
        device.get_dac().write(addr=2, voltage=5.0)
        device.get_dac().load_all_channels().wait()

    def disable_fullbridge():
        device.get_dac().write(addr=0, voltage=0.0)
        device.get_dac().write(addr=1, voltage=0.0)
        device.get_dac().write(addr=2, voltage=0.0)
        device.get_dac().load_all_channels().wait()

    def set_positive_polarity():
        device.get_dac().write(addr=4, voltage=0.0)
        device.get_dac().write(addr=5, voltage=0.0)
        device.get_dac().write(addr=6, voltage=0.0)
        device.get_dac().load_all_channels().wait()

    def set_negative_polarity():
        device.get_dac().write(addr=4, voltage=5.0)
        device.get_dac().write(addr=5, voltage=5.0)
        device.get_dac().write(addr=6, voltage=5.0)
        device.get_dac().load_all_channels().wait()

    client.start_cyclic_spi_channel_transfer()
    print("cyclic spi channel transfer started")

    device.initialize().wait()
    print("Enclosure initialized.")

    input("Positive Polarity Test. Press enter to continue...")
    set_positive_polarity()
    enable_fullbridge()

    input("Negative Polarity Test. Press enter to continue...")
    set_negative_polarity()
    enable_fullbridge()

    input("PWM Disable Test. Press enter to continue...")
    set_negative_polarity()
    disable_fullbridge()

    input("Reset. Press enter to continue...")
    for addr in range(8):
        device.get_dac().write(addr=addr, voltage=0.0)
    device.get_dac().load_all_channels().wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
