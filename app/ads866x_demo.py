if __name__ == "__main__":
    from time import sleep

    from spi_master.ch341 import CH341 as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.adc.ads866x import Ads866x

    device = Ads866x()

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

    client.stop_cyclic_spi_channel_transfer()

    del client
