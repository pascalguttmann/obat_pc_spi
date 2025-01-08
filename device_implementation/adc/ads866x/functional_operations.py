from typing import Any
from bitarray import bitarray

from spi_operation import SequenceTransferOperation
import register_operations as op


class Initialize(SequenceTransferOperation):
    pass


class ReadVoltage(op.Ads866xSingleTransferOperation):
    """Read the quantized analog voltage from the adc."""

    def __init__(self):
        super().__init__(response_required=True)

    def _parse_response(self, rsp: bitarray) -> Any:
        _ = rsp
        raise NotImplementedError
