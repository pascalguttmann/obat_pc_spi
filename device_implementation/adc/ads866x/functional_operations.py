from typing import Any, List
from bitarray import bitarray
from enum import Enum

from util import bitarray_to_uint
from spi_operation import SequenceTransferOperation
import device_implementation.adc.ads866x.register_operations as op
import device_implementation.adc.ads866x.registers as reg


class Ads866xInputRange(Enum):
    BIPOLAR_12V288 = reg.RangeSelReg().RANGE_SEL.const["BIPOLAR_12V288"]
    BIPOLAR_10V24 = reg.RangeSelReg().RANGE_SEL.const["BIPOLAR_10V24"]
    BIPOLAR_6V144 = reg.RangeSelReg().RANGE_SEL.const["BIPOLAR_6V144"]
    BIPOLAR_5V12 = reg.RangeSelReg().RANGE_SEL.const["BIPOLAR_5V12"]
    BIPOLAR_2V56 = reg.RangeSelReg().RANGE_SEL.const["BIPOLAR_2V56"]
    UNIPOLAR_12V288 = reg.RangeSelReg().RANGE_SEL.const["UNIPOLAR_12V288"]
    UNIPOLAR_10V24 = reg.RangeSelReg().RANGE_SEL.const["UNIPOLAR_10V24"]
    UNIPOLAR_6V144 = reg.RangeSelReg().RANGE_SEL.const["UNIPOLAR_6V144"]
    UNIPOLAR_5V12 = reg.RangeSelReg().RANGE_SEL.const["UNIPOLAR_5V12"]


class Ads866xGpoVal(Enum):
    HIGH = reg.SdoCtlReg().GPO_VAL.const["HIGH"]
    LOW = reg.SdoCtlReg().GPO_VAL.const["LOW"]


class Initialize(SequenceTransferOperation):
    """Initialize the Ads866x adc"""

    def __init__(self, input_range: Ads866xInputRange):
        """Initialize the adc with the specified input range.

        :param input_range: InputRange enum specifying the input range setting.
        """
        ops = []

        RST_PWRCTL_REG = reg.RstPwrctlReg()
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.WKEY.slice] = RST_PWRCTL_REG.WKEY.const[
            "PROTECTION_KEY"
        ]
        ops.append(
            op.WriteHword(
                RST_PWRCTL_REG.address_lower_halfword_ba, RST_PWRCTL_REG.data[0:16]
            )
        )

        RST_PWRCTL_REG = reg.RstPwrctlReg()
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.WKEY.slice] = RST_PWRCTL_REG.WKEY.const[
            "PROTECTION_KEY"
        ]
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.VDD_AL_DIS.slice] = (
            RST_PWRCTL_REG.VDD_AL_DIS.const["VDD_AL_ENABLED"]
        )
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.IN_AL_DIS.slice] = (
            RST_PWRCTL_REG.IN_AL_DIS.const["IN_AL_ENABLED"]
        )
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.RSTN_APP.slice] = (
            RST_PWRCTL_REG.RSTN_APP.const["RSTN_POR"]
        )
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.NAP_EN.slice] = RST_PWRCTL_REG.NAP_EN.const[
            "NAP_DISABLED"
        ]
        RST_PWRCTL_REG.data[RST_PWRCTL_REG.PWRDN.slice] = RST_PWRCTL_REG.PWRDN.const[
            "MODE_ACTIVE"
        ]
        ops.append(
            op.WriteHword(
                RST_PWRCTL_REG.address_lower_halfword_ba, RST_PWRCTL_REG.data[0:16]
            )
        )

        SDI_CTL_REG = reg.SdiCtlReg()
        SDI_CTL_REG.data[SDI_CTL_REG.SDI_MODE.slice] = SDI_CTL_REG.SDI_MODE.const[
            "SPI_MODE_0_CPOL_0_CPHA_0"
        ]
        ops.append(
            op.WriteVerifyWord(addr=SDI_CTL_REG.address_ba, data=SDI_CTL_REG.data)
        )

        SDO_CTL_REG = reg.SdoCtlReg()
        SDO_CTL_REG.data[SDO_CTL_REG.GPO_VAL.slice] = SDO_CTL_REG.GPO_VAL.const["LOW"]
        SDO_CTL_REG.data[SDO_CTL_REG.SDO1_CONFIG.slice] = SDO_CTL_REG.SDO1_CONFIG.const[
            "SDO1_GPO"
        ]
        SDO_CTL_REG.data[SDO_CTL_REG.SSYNC_CLK.slice] = SDO_CTL_REG.SSYNC_CLK.const[
            "CLK_EXT"
        ]
        SDO_CTL_REG.data[SDO_CTL_REG.SDO_MODE.slice] = SDO_CTL_REG.SDO_MODE.const[
            "SDO_DEFAULT_CLK"
        ]
        ops.append(
            op.WriteVerifyWord(addr=SDO_CTL_REG.address_ba, data=SDO_CTL_REG.data)
        )

        DATAOUT_CTL_REG = reg.DataOutCtlReg()
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.DEVICE_ADDR_INCL.slice] = (
            DATAOUT_CTL_REG.DEVICE_ADDR_INCL.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.VDD_ACTIVE_L_ALARM_INCL.slice] = (
            DATAOUT_CTL_REG.VDD_ACTIVE_L_ALARM_INCL.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.VDD_ACTIVE_H_ALARM_INCL.slice] = (
            DATAOUT_CTL_REG.VDD_ACTIVE_H_ALARM_INCL.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.IN_ACTIVE_L_ALARM_INCL.slice] = (
            DATAOUT_CTL_REG.IN_ACTIVE_L_ALARM_INCL.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.IN_ACTIVE_H_ALARM_INCL.slice] = (
            DATAOUT_CTL_REG.IN_ACTIVE_H_ALARM_INCL.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.RANGE_INCL.slice] = (
            DATAOUT_CTL_REG.RANGE_INCL.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.PAR_EN.slice] = (
            DATAOUT_CTL_REG.PAR_EN.const["INCLUDE"]
        )
        DATAOUT_CTL_REG.data[DATAOUT_CTL_REG.DATA_VAL.slice] = (
            DATAOUT_CTL_REG.DATA_VAL.const["CONVERSION_RESULT"]
        )
        ops.append(
            op.WriteVerifyWord(
                addr=DATAOUT_CTL_REG.address_ba, data=DATAOUT_CTL_REG.data
            )
        )

        RANGE_SEL_REG = reg.RangeSelReg()
        RANGE_SEL_REG.data[RANGE_SEL_REG.INTREF_DIS.slice] = (
            RANGE_SEL_REG.INTREF_DIS.const["INTREF_ENABLE"]
        )
        RANGE_SEL_REG.data[RANGE_SEL_REG.RANGE_SEL.slice] = input_range.value
        ops.append(
            op.WriteVerifyWord(addr=RANGE_SEL_REG.address_ba, data=RANGE_SEL_REG.data)
        )

        super().__init__(ops)

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        :return: None
        """
        if not len(operations_rsp) == 6:
            raise ValueError(
                f"Initialize expected list of 6 responses, but got {operations_rsp=}"
            )

        if not all(operations_rsp[2:]):
            raise ValueError(
                f"Initialize WriteVerifyRegister failed. Returns: {operations_rsp[2:]=}"
            )

        return None


class ReadVoltage(op.Ads866xSingleTransferOperation):
    """Read the quantized analog voltage from the adc."""

    def __init__(self):
        super().__init__(response_required=True)

    def _parse_response(self, rsp: bitarray) -> Any:
        if not len(rsp) == 32:
            raise ValueError(
                f"WriteVerifyWord expected sub operations 32-Bit bitarray, but got {len(rsp)=}"
            )

        conv_result = rsp[20:32]
        device_addr = rsp[16:20]
        avdd_alaram = rsp[14:16]
        input_alarm = rsp[12:14]
        input_range = rsp[8:12]
        parity_bits = rsp[6:8]
        _ = rsp[0:6]

        data_frame_parity_bit = parity_bits[0:1]
        conv_result_parity_bit = parity_bits[1:2]

        if not self._check_even_parity(conv_result_parity_bit + conv_result):
            raise ValueError("ReadVoltage expected even parity for conversion_result.")

        if not self._check_even_parity(data_frame_parity_bit + rsp[8:32]):
            raise ValueError("ReadVoltage expected even parity for frame.")

        _ = device_addr
        _ = avdd_alaram
        _ = input_alarm

        match input_range:
            case Ads866xInputRange.BIPOLAR_12V288:
                sens_V_per_lsb = 0.006
                n_offset = 2**11
            case Ads866xInputRange.BIPOLAR_10V24:
                sens_V_per_lsb = 0.005
                n_offset = 2**11
            case Ads866xInputRange.BIPOLAR_6V144:
                sens_V_per_lsb = 0.003
                n_offset = 2**11
            case Ads866xInputRange.BIPOLAR_5V12:
                sens_V_per_lsb = 0.0025
                n_offset = 2**11
            case Ads866xInputRange.BIPOLAR_2V56:
                sens_V_per_lsb = 0.00125
                n_offset = 2**11
            case Ads866xInputRange.UNIPOLAR_12V288:
                sens_V_per_lsb = 0.003
                n_offset = 0
            case Ads866xInputRange.UNIPOLAR_10V24:
                sens_V_per_lsb = 0.0025
                n_offset = 0
            case Ads866xInputRange.UNIPOLAR_6V144:
                sens_V_per_lsb = 0.0015
                n_offset = 0
            case Ads866xInputRange.UNIPOLAR_5V12:
                sens_V_per_lsb = 0.00125
                n_offset = 0
            case _:
                raise ValueError(f"ReadVoltage Unknown input_range {input_range}.")

        return float(sens_V_per_lsb * (bitarray_to_uint(conv_result) - n_offset))

    def _check_even_parity(self, ba: bitarray) -> bool:
        return ba.count() % 2 == 0


class SetGpo(op.SetHword):
    """Set the general purpose output of the ADC."""

    def __init__(self):
        SDO_CTL_REG = reg.SdoCtlReg()
        SDO_CTL_REG.data[SDO_CTL_REG.GPO_VAL.slice] = bitarray("1")

        super().__init__(
            addr=SDO_CTL_REG.address_lower_halfword_ba, data=SDO_CTL_REG.data[0:16]
        )


class ClearGpo(op.ClearHword):
    """Clear the general purpose output of the ADC."""

    def __init__(self):
        SDO_CTL_REG = reg.SdoCtlReg()
        SDO_CTL_REG.data[SDO_CTL_REG.GPO_VAL.slice] = bitarray("1")

        super().__init__(
            addr=SDO_CTL_REG.address_lower_halfword_ba, data=SDO_CTL_REG.data[0:16]
        )
