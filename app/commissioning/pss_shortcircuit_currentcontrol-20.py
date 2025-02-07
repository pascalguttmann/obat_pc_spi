if __name__ == "__main__":
    from time import sleep
    from spi_master.arduino_spi import ArduinoSpi as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.pss import Pss, PssTrackingMode

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

    device.write_config(
        tracking_mode=PssTrackingMode.current,
        target_voltage=2.0,
        target_current=-20.0,
        lower_voltage_limit=+0.0,
        upper_voltage_limit=+4.0,
        lower_current_limit=-10.0,
        upper_current_limit=+10.0,
    ).wait()

    device.output_connect().wait()
    sleep(0.1)
    voltage, current = device.read_output().get_result_after_wait()
    input(
        f"Output connected, Pss measured output as: {voltage:.6f} V, {current:.6f} A. Press enter to disconnect and finish."
    )
    device.output_disconnect().wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
