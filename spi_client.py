"""Spi client for debugging and demonstration. Client will create an instance
of the spi driver server for a given hardware spi interface and connect to it.
Arbitrary data can be sent and received using the client."""
(
    client_to_server_pipe,
    server_to_client_pipe,
    server_read,
    server_write,
    b64_server_ipc as ipc,
    pack_server_response,
    unpack_server_command,
)

from spi_driver_ipc import (
    b64_client_ipc as ipc,
    client_to_server_pipe,
    server_to_client_pipe,
    client_read_pipe_end,
    client_write_pipe_end,
    pack_server_command,
    unpack_server_response,

)
from spi_server import SpiServer
from ch341.ch341 import CH341

with SpiServer(CH341()) as spi_server:
    with client_write_pipe_end as wr:
        with client_read_pipe_end as rd:
    

            try:
                while True:
                    user_input = input("Enter something (or 'quit' to exit): ")
                    if user_input.lower() == "quit":
                        print("Exiting program.")
                        break
                    # Process the user input here
                    print("You entered:", user_input)
            except KeyboardInterrupt:
                print("SIGINT: Exiting program.")

            if __name__ == "__main__":

                import argparse

                parser = argparse.ArgumentParser()
                parser.add_argument(
                    "spi_master", help="The device used as an spi master. E.g. ch34x_pis1"
                )

                spi_server = SpiServer(spi_master=sys.argv[1])
