from ch341.ch341 import CH341

ch341 = CH341()
tx_buf = bytearray([0x55])
rx_buf = ch341.transfer(cs=0, buf=tx_buf)

print(f"TX: {tx_buf}\nRX: {rx_buf}")
