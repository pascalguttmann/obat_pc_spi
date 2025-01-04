from bitarray import bitarray
from typing import Optional, Any

from operation_base import OperationBase


class SingleTransferOperation(OperationBase):
    def __init__(
        self,
        command: bitarray,
        response: Optional[bitarray] = None,
        response_required: bool = True,
    ) -> None:
        self._command = command
        self._response_required = response_required
        if response:
            self.set_response(response)
        else:
            self._response = None

    def _parse_response(self, rsp: bitarray) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation."""
        _ = rsp
        raise NotImplementedError("SingleTransferOperation does not implement")

    def __len__(self) -> int:
        return len(self.get_command())

    def __repr__(self) -> str:
        return f"SingleTransferOperation: command={self._command}, response={self._response}, response_required={self._response_required}"

    def set_response(self, response: bitarray) -> None:
        if not self._response_required:
            raise ValueError("operation does not require a response.")
        if len(self._command) != len(response):
            raise ValueError(
                "command and response of operation must be of same length."
            )
        self._response = response

    def get_response(self) -> Optional[bitarray]:
        return self._response

    def get_parsed_response(self) -> Any:
        rsp = self.get_response()
        if not rsp:
            raise ValueError("SingleTransferOperation does not have a response.")
        return self._parse_response(rsp)

    def get_command(self) -> bitarray:
        return self._command

    def get_response_required(self) -> bool:
        return self._response_required
