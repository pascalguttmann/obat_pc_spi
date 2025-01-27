if __name__ == "__main__":
    from time import sleep

    # TODO: Abstract spi_master spi_client_server and channels into "ObatApp" class
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

    client.start_cyclic_spi_channel_transfer()

    print(device.initialize().wait())

    device.write_config(
        tracking_mode=PssTrackingMode.voltage,
        target_voltage=3.0,
        lower_current_limit=-1.0,
        upper_current_limit=+1.0,
    ).wait()

    device.output_connect()
    sleep(1.0)
    device.output_disconnect()

    client.stop_cyclic_spi_channel_transfer()

    del client
