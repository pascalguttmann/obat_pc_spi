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

    device.initialize()
    read_volt_adc_voltage_op = device.get_volt_adc().read()
    read_curr_adc_voltage_op = device.get_curr_adc().read()

    client.start_cyclic_spi_channel_transfer()
    print("cyclic spi channel transfer started")

    voltage_adc = read_volt_adc_voltage_op.get_result_after_wait()
    current_adc = read_curr_adc_voltage_op.get_result_after_wait()
    print(
        f"Pss:\n\t'Volt Adc' Voltage={voltage_adc:.6f} V\n\t'Curr Adc` Voltage={current_adc:6f} V"
    )

    client.stop_cyclic_spi_channel_transfer()

    del client
