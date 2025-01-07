"""Texas Instruments
ADS866x 12-Bit, High-Speed, Single-Supply, SAR ADC Data Acquisition System With
Programmable, Bipolar Input Ranges

- ADS8661: 1.25 MSPS
- ADS8665: 500 kSPS
- Software programmable input ranges:
    – Bipolar ranges: ±12.288 V, ±10.24 V, ±6.144 V, ±5.12 V, and ±2.56 V
    – Unipolar ranges: 0 V–12.288 V, 0 V–10.24 V, 0 V–6.144 V, and 0 V–5.12 V

Datasheet: https://www.ti.com/lit/ds/symlink/ads8661.pdf
"""

from adc_base import AdcBase

import operations as op


class Ads866x(AdcBase):
    pass

    # SDO-0 single output for daisychain, with external clock
    # SDO_CTL_REG bits 7-0 program to 0x00
    #
    # conversion start at rising edge of CS.
