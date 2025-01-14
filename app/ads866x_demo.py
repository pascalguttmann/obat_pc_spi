if __name__ == "__main__":
    from time import sleep
    import threading

    from spi_master.ch341 import CH341 as SpiMaster
    from spi_client_server import SpiChannel, SpiClient, SpiServer
    from device_implementation.adc.ads866x import Ads866x, Ads866xGpoVal

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

    count = 0
    stop_event = threading.Event()
    while not stop_event.is_set():
        try:
            if count % 2 == 0:
                device.write_gpo(callback=None, gpo_val=Ads866xGpoVal.HIGH)
            else:
                device.write_gpo(callback=None, gpo_val=Ads866xGpoVal.LOW)
            count += 1
            print(f"Ads866x.read()= {device.read().wait():.3f} V")
            sleep(0.25)
        except KeyboardInterrupt:
            stop_event.set()

    client.stop_cyclic_spi_channel_transfer()

    del client
