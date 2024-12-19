import sys

from ch341.ch341 import CH341


def hex_to_bytearray(hex_string):
    bytes_object = bytes.fromhex(hex_string)
    bytearray_object = bytearray(bytes_object)
    return bytearray_object


hex_string = sys.argv[1]
tx_arg = hex_to_bytearray(hex_string)
print(f"bytearray: {tx_arg.hex()}")
ch341 = CH341()
tx_buf = tx_arg
rx_buf = ch341.transfer(cs=0, buf=tx_buf)
print(f"TX: 0x{tx_buf.hex()}")
print(f"RX: 0x{rx_buf.hex()}")
