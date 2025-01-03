from bitarray import bitarray
from typing import Optional


class SingleTransferOperation:
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

    def get_command(self) -> bitarray:
        return self._command

    def get_response_required(self) -> bool:
        return self._response_required
