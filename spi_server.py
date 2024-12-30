from spi_driver_ipc import (
    client_to_server_pipe,
    server_to_client_pipe,
    server_read_pipe_end,
    server_write_pipe_end,
    b64_server_ipc as ipc,
    pack_server_response,
    unpack_server_command,
)
from spi_master_base import SpiMasterBase

import multiprocessing
import signal
import os


class SpiServer:
    def __init__(self, spi_master: SpiMasterBase) -> None:
        self._spi_master: SpiMasterBase = spi_master
        self._subprocess = None
        return

    def __enter__(self):
        return self.start_server_process()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return self.stop_server_process()

    def start_server_process(self):
        self._subprocess = multiprocessing.Process(target=self.setup)
        self._subprocess.start()
        return self

    def stop_server_process(self):
        if self._subprocess:
            os.kill(self._subprocess.pid, signal.SIGINT)
            self._subprocess.join()

    def setup(self):
        with client_to_server_pipe:
            with server_to_client_pipe:
                with server_read_pipe_end:
                    with server_write_pipe_end:
                        print("SpiServer: running")
                        self._spi_master.init()
                        print("SpiServer: SpiMaster initialized")
                        return self.run()

    def transfer(self, cs: int, buf: bytearray) -> bytearray:
        return self._spi_master.transfer(cs, buf)

    def run(self):
        try:
            while True:
                ipc_read = ipc.read()
                cs, spi_tx = unpack_server_command(ipc_read)
                spi_rx = self._spi_master.transfer(cs, spi_tx)
                ipc.write(pack_server_response(spi_rx))
                print(f"SpiServer: {cs=}, {spi_tx=}, {spi_rx=}\n")

        except KeyboardInterrupt:
            print("SpiServer: SIGINT")
