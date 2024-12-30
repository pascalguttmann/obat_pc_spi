import sys

from ch341.ch341 import CH341


def hex_to_bytearray(hex_string):
    bytearray_object = bytearray.fromhex(hex_string)
    bytearray_object = bytearray(bytearray_object)
    return bytearray_object


hex_string = sys.argv[1]
tx_buf = hex_to_bytearray(hex_string)
ch341 = CH341()
ch341.init()
rx_buf = ch341.transfer(cs=0, buf=tx_buf)
print(f"TX: 0x{tx_buf.hex()}")
print(f"RX: 0x{rx_buf.hex()}")
