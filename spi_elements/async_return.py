from typing import Any, Callable, Optional
import threading


class AsyncReturn:
    def __init__(self, ext_callback: Optional[Callable[..., None]] = None) -> None:
        self._callback = ext_callback
        self._callback_finished = threading.Event()
        self._result = None

    def _wrap_callback(
        self, callback: Optional[Callable[..., None]]
    ) -> Callable[..., None]:
        def wrapper(*args) -> None:
            if len(args) == 1:
                self._result = args[0]
            else:
                self._result = args
            if callback:
                _ = callback(*args)
            self._callback_finished.set()
            return None

        return wrapper

    def wait(self) -> Any:
        self._callback_finished.wait()
        return self._result

    def get_callback(self) -> Callable[..., None]:
        return self._wrap_callback(self._callback)

    def is_finished(self) -> bool:
        return self._callback_finished.is_set()

    def get_result(self) -> Any:
        if self.is_finished():
            return self._result
        else:
            raise RuntimeError("AsyncReturn: Result not available yet.")

    def get_result_after_wait(self) -> Any:
        self.wait()
        return self._result

    def __repr__(self) -> str:
        return f"AsyncReturn(is_finished={self._callback_finished.is_set()}, result={self._result}, callback={self._callback})"
