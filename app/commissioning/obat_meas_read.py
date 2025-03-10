if __name__ == "__main__":
    from spi_master.arduino_spi import ArduinoSpi as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.obat import (
        Obat,
        EnclosurePeltierPolarity,
        PssTrackingMode,
    )

    import keyboard
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

    device.get_pss().write_config(
        tracking_mode=PssTrackingMode.voltage,
        target_voltage=3.0,
        target_current=1.0,
        lower_voltage_limit=+0.0,
        upper_voltage_limit=+4.0,
        lower_current_limit=-10.0,
        upper_current_limit=+10.0,
    ).wait()

    device.get_pss().output_connect().wait()
    sleep(0.1)

    while not keyboard.is_pressed("enter"):
        (voltage, current, temperature) = device.get_meas().read().wait()

        print(
            f"Meas:\tVoltage={voltage:.6f} V\tCurrent={current:6f} A\tTemperature={temperature:6f} °C\tPress enter to stop."
        )
        sleep(0.5)

    device.get_pss().output_disconnect().wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
