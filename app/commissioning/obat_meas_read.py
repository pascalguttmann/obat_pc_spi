if __name__ == "__main__":
    from spi_master.arduino_spi import ArduinoSpi as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.obat import Obat, EnclosurePeltierPolarity

    from time import sleep

    device = Obat().get_meas()

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

    try:
        while True:
            (voltage, current, temperature) = device.read().wait()

            print(
                f"Meas:\tVoltage={voltage:.6f} V\tCurrent={current:6f} A\tTemperature={temperature:6f} °C"
            )
            sleep(0.5)
    except KeyboardInterrupt:
        pass

    client.stop_cyclic_spi_channel_transfer()

    del client
