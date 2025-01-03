import unittest


from spi_master.virtual.virtual import Virtual


class TestVirtual(unittest.TestCase):
    def test_transfer_fallback(self):
        virt_spi_master = Virtual()
        cs: int = 0
        tx_buf: bytearray = bytearray(b"BABE")

        virt_spi_master.init()

        rx_buf: bytearray = virt_spi_master.transfer(cs, tx_buf)
        self.assertIsInstance(rx_buf, bytearray)
        self.assertEqual(rx_buf, bytearray(b"\x00\x00\x00\x00"))

        rx_buf: bytearray = virt_spi_master.transfer(cs, tx_buf)
        self.assertIsInstance(rx_buf, bytearray)
        self.assertEqual(rx_buf, bytearray(b"\x00\x00\x00\x01"))

        rx_buf: bytearray = virt_spi_master.transfer(cs, tx_buf)
        self.assertIsInstance(rx_buf, bytearray)
        self.assertEqual(rx_buf, bytearray(b"\x00\x00\x00\x02"))

    def test_raise_exception_transfer_without_init(self):
        virt_spi_master = Virtual()
        cs: int = 0
        tx_buf: bytearray = bytearray(b"BABE")

        with self.assertRaises(RuntimeError):
            rx_buf: bytearray = virt_spi_master.transfer(cs, tx_buf)
