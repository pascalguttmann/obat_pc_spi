from xp_named_pipe import NamedPipe, ReadPipeEnd, WritePipeEnd
from xp_named_pipe.base64_encoder_decoder import Base64DatagrammeEncoderDecoder as B64

from typing import Tuple

client_to_server_pipe: NamedPipe = NamedPipe("./ipc/client_to_server")
server_to_client_pipe: NamedPipe = NamedPipe("./ipc/server_to_client")

client_read_pipe_end = ReadPipeEnd(server_to_client_pipe)
client_write_pipe_end = WritePipeEnd(client_to_server_pipe)

server_read_pipe_end = ReadPipeEnd(client_to_server_pipe)
server_write_pipe_end = WritePipeEnd(server_to_client_pipe)

b64_client_ipc = B64(
    read_func=client_read_pipe_end.read(),
    write_func=client_write_pipe_end.write(),
)

b64_server_ipc = B64(
    read_func=server_read_pipe_end.read(),
    write_func=server_write_pipe_end.write(),
)


def pack_server_command(cs: int, buf: bytearray) -> bytearray:
    return bytearray(cs.to_bytes(1, "big", signed=False) + buf)


def unpack_server_command(cmd: bytearray) -> Tuple[int, bytearray]:
    return cmd[0], cmd[1:]


def pack_server_response(buf: bytearray) -> bytearray:
    return buf


def unpack_server_response(response: bytearray) -> bytearray:
    return response
