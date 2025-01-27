if __name__ == "__main__":
    from time import sleep

    from spi_master.ch341 import CH341 as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.pss import Pss, PssTrackingMode

    device = Pss()

    client = SpiClient(
        spi_server=SpiServer(SpiMaster()),
        spi_channels=[
            SpiChannel(
                spi_operation_request_iterator=device, transfer_interval=0.1, cs=0
            )
        ],
    )

    target_voltage = 3.6
    maximum_charge_current = 1.6
    threshold_current = 0.05

    client.start_cyclic_spi_channel_transfer()

    device.initialize().wait()
    device.write_config(
        tracking_mode=PssTrackingMode.voltage,
        target_voltage=target_voltage,
        lower_current_limit=0.0,
        upper_current_limit=maximum_charge_current,
    ).wait()

    device.output_connect().wait()

    voltage, current = device.read_output().wait()
    while current > threshold_current:
        sleep(1.0)

    device.output_disconnect().wait()

    client.stop_cyclic_spi_channel_transfer()

    del client
