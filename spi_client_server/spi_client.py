from dataclasses import dataclass
from typing import Callable, List, Sequence, Optional
import time
import threading
from bitarray import bitarray

from spi_elements.spi_operation_request_iterator import SingleTransferOperationRequest
from util import reverse_string
from spi_client_server.spi_driver_ipc import (
    b64_client_ipc as ipc,
    client_read_pipe_end,
    client_write_pipe_end,
    pack_server_command,
    unpack_server_response,
)
from spi_client_server.spi_server import SpiServer
from spi_elements import SpiOperationRequestIteratorBase


@dataclass
class SpiChannel:
    spi_operation_request_iterator: SpiOperationRequestIteratorBase
    transfer_interval: float
    cs: int
    pre_transfer_channel_initialization: Optional[Sequence[bitarray]] = None


class SpiClient:
    """Automatic SpiClient, which instantiates its own SpiServer to send SpiCommands to."""

    def __init__(self, spi_server: SpiServer, spi_channels: List[SpiChannel]) -> None:
        self._spi_server_lock = threading.Lock()
        if len(spi_channels) < 1:
            raise ValueError("At least one SpiChannel must be specified.")
        else:
            self._spi_channels = list(enumerate(spi_channels))
            self._spi_channel_threads = [
                self._create_cyclic_locking_thread(
                    lambda: self._transfer_spi_channel(spi_channel, ch_id),
                    spi_channel.transfer_interval,
                )
                for (ch_id, spi_channel) in self._spi_channels
            ]
            self._spi_channel_threads_run_flag = False
            self._spi_channels_delay_buffer: List[
                SingleTransferOperationRequest | None
            ] = [None] * len(self._spi_channels)
        self._spi_server = spi_server
        self._spi_server.start_server_process()
        client_write_pipe_end.open()
        client_read_pipe_end.open()

        for ch in spi_channels:
            if ch.pre_transfer_channel_initialization is not None:
                self._initialize_spi_channel(ch)

    def __del__(self):
        self._spi_server.stop_server_process()
        client_write_pipe_end.close()
        client_read_pipe_end.close()

    def get_spi_server(self) -> SpiServer:
        return self._spi_server

    def start_cyclic_spi_channel_transfer(self) -> None:
        self._spi_channel_threads_run_flag = True
        for ch in self._spi_channel_threads:
            ch.start()

    def stop_cyclic_spi_channel_transfer(self) -> None:
        self._spi_channel_threads_run_flag = False
        for ch in self._spi_channel_threads:
            ch.join()

    def _create_cyclic_locking_thread(
        self, func: Callable[[], None], interval: float
    ) -> threading.Thread:
        def cyclic_locking_wrapper():
            last_time = time.perf_counter()
            while self._spi_channel_threads_run_flag:
                with self._spi_server_lock:
                    func()
                current_time = time.perf_counter()
                sleep_time = interval - (current_time - last_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                last_time = current_time

        return threading.Thread(target=cyclic_locking_wrapper, daemon=True)

    def _write_to_spi_server(self, cs: int, buf: bytearray) -> None:
        return ipc.write(pack_server_command(cs, buf))

    def _read_from_spi_server(self) -> bytearray:
        return unpack_server_response(ipc.read())

    def _transfer_spi_channel(self, spi_channel: SpiChannel, ch_id: int) -> None:
        new_op_req = next(spi_channel.spi_operation_request_iterator)

        rx = self._transfer_spi_data(spi_channel.cs, new_op_req.operation.get_command())

        old_op_req = self._spi_channels_delay_buffer[ch_id]
        if old_op_req:
            if old_op_req.operation.get_response_required():
                old_op_req.operation.set_response(rx)
            else:
                _ = rx

            if old_op_req.callback:
                old_op_req.callback(old_op_req.operation.get_parsed_response())

        self._spi_channels_delay_buffer[ch_id] = new_op_req

        return

    def _transfer_spi_data(self, cs: int, data: bitarray) -> bitarray:
        tx: bytearray = bytearray(data[::-1].tobytes())
        self._write_to_spi_server(cs, tx)

        rx: bytearray = self._read_from_spi_server()
        return bitarray(reverse_string("".join(format(byte, "08b") for byte in rx)))

    def _initialize_spi_channel(self, spi_channel: SpiChannel) -> None:
        if spi_channel.pre_transfer_channel_initialization is None:
            raise ValueError(
                "SpiChannel must have a pre_transfer_channel_initialization for channel initialization."
            )

        for ba in spi_channel.pre_transfer_channel_initialization:
            _ = self._transfer_spi_data(spi_channel.cs, ba)
