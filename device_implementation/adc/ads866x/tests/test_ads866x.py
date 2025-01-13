import unittest

from device_implementation.adc.ads866x import Ads866x


class TestAds866x(unittest.TestCase):
    def test_init(self):
        _ = Ads866x()
