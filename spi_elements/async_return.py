from typing import Any, Callable, Optional
import threading


class AsyncReturn:
    def __init__(self, ext_callback: Optional[Callable[..., None]] = None) -> None:
        self._callback = self._wrap_callback(ext_callback)
        self._callback_finished = threading.Event()
        self._result = None

    def _wrap_callback(
        self, callback: Optional[Callable[..., None]]
    ) -> Callable[..., None]:
        def wrapper(*args, **kw_args) -> None:
            self._result = (*args, *kw_args)
            if callback:
                _ = callback(*args, **kw_args)
            self._callback_finished.set()
            return None

        return wrapper

    def wait(self) -> Any:
        self._callback_finished.wait()
        return self._result

    def get_callback(self) -> Callable[..., None]:
        return self._callback

    def is_finished(self) -> bool:
        return self._callback_finished.is_set()

    def get_result(self) -> Any:
        if self.is_finished():
            return self._result
        else:
            raise RuntimeError("AsyncReturn: Result not available yet.")
