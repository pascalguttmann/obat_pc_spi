"""Spi client for debugging and demonstration. Client will create an instance
of the spi driver server for a given hardware spi interface and connect to it.
Arbitrary data can be sent and received using the client."""

if __name__ == "__main__":

    import sys
    import os

    sys.path.append(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "python_xp_named_pipe/",
        )
    )

    from spi_client_server.spi_driver_ipc import (
        b64_client_ipc as ipc,
        client_read_pipe_end,
        client_write_pipe_end,
        pack_server_command,
        unpack_server_response,
    )
    from spi_client_server.spi_server import SpiServer
    from spi_master.ch341.ch341 import CH341

    def hex_string_to_bytearray(hex_string):
        if hex_string.startswith("0x"):
            hex_string = hex_string[2:]

        if len(hex_string) % 2 != 0:
            hex_string = "0" + hex_string

        return bytearray.fromhex(hex_string)

    with SpiServer(CH341()) as spi_server:
        with client_write_pipe_end:
            with client_read_pipe_end:

                cs = 0

                try:
                    while True:
                        user_input = input("Enter hexstring or 'exit': ")
                        if user_input.lower() == "exit":
                            print("Exiting program.")
                            break
                        tx_bytearray = hex_string_to_bytearray(user_input)

                        ipc.write(pack_server_command(cs, tx_bytearray))
                        rx_bytearray = unpack_server_response(ipc.read())

                        print(f"TX: {tx_bytearray.hex()}, RX: {rx_bytearray.hex()}")

                except KeyboardInterrupt:
                    print("SIGINT: Exiting program.")
