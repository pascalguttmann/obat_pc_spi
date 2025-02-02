from arduino_spi import ArduinoSpi


def hex_string_to_bytearray(hex_string):
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]

    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string

    return bytearray.fromhex(hex_string)


ard = ArduinoSpi()
ard.init()

try:
    while True:
        user_input = input("Enter hexstring or 'exit': ")
        if user_input.lower() == "exit":
            print("Exiting program.")
            break
        tx_bytearray = hex_string_to_bytearray(user_input)

        rx_bytearray = ard.transfer(cs=0, buf=tx_bytearray)

        print(f"TX: 0x{tx_bytearray.hex()}, RX: 0x{rx_bytearray.hex()}")

except KeyboardInterrupt:
    print("SIGINT: Exiting program.")
