import unittest
import threading

from async_return import AsyncReturn

callback_called = threading.Event()


def callback(*args, **kw_args):
    _ = *args, *kw_args
    callback_called.set()
    return None


class TestAsyncReturn(unittest.TestCase):
    def test_init(self):
        ar = AsyncReturn(callback)
        self.assertNotEqual(ar._callback, callback)
        self.assertFalse(ar._callback_finished.is_set())
        self.assertIsNone(ar._result)

        self.assertFalse(callback_called.is_set())
        clbk = ar.get_callback()
        clbk(None)
        self.assertTrue(callback_called.is_set())

    def test_is_finished(self):
        ar = AsyncReturn()
        self.assertFalse(ar.is_finished())
        ar.get_callback()(None)
        self.assertTrue(ar.is_finished())

    def test_get_result_001(self):
        with self.assertRaises(RuntimeError):
            ar = AsyncReturn()
            self.assertFalse(ar.is_finished())
            _ = ar.get_result()

    def test_get_result_002(self):
        ar = AsyncReturn()
        ar.get_callback()(42, 0xDA1A)
        res = ar.get_result()
        self.assertEqual(res, (42, 0xDA1A))

    def test_get_result_003(self):
        ar = AsyncReturn()
        ar.get_callback()(42)
        res = ar.get_result()
        self.assertEqual(res, 42)

    def test_wait(self):
        ar = AsyncReturn()
        ar.get_callback()(42, 0xDA1A)
        res = ar.wait()
        self.assertEqual(res, (42, 0xDA1A))
