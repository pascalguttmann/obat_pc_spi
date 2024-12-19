import os
import re
import sys

from ctypes import (
    CDLL,
    POINTER,
    c_bool,
    c_char_p,
    c_int32,
    c_uint,
    c_uint8,
    c_uint32,
    c_void_p,
    cdll,
    windll,
)
from functools import lru_cache
from typing import Optional


@lru_cache(maxsize=1)
def load_CH341DLL() -> CDLL:
    dll_name = os.getenv("CH341DLL")
    if dll_name is None:
        if sys.platform == "win32":
            dll_name = "CH341DLLA64.dll" if sys.maxsize > 2147483647 else "CH341DLL.dll"
        else:
            dll_name = "libch347.so"

    return load(dll_name)


def load(dll_name: str) -> CDLL:
    if sys.platform == "win32":
        return load_win(dll_name)
    else:
        return load_posix(dll_name)


def load_win(dll_name: str) -> CDLL:
    return windll.LoadLibrary(dll_name)


def load_posix(dll_name: str) -> CDLL:
    dll = cdll.LoadLibrary(dll_name)

    funcs = [
        {"name": "CH34xOpenDevice", "argtypes": (c_char_p,), "restype": c_int32},
        {"name": "CH34xCloseDevice", "argtypes": (c_int32,), "restype": c_bool},
        {
            "name": "CH34x_GetDriverVersion",
            "argtypes": (c_int32, c_char_p),
            "restype": c_bool,
        },
        {
            "name": "CH34x_GetChipVersion",
            "argtypes": (c_int32, c_char_p),
            "restype": c_bool,
        },
        {
            "name": "CH34x_GetChipType",
            "argtypes": (c_int32, POINTER(c_uint32)),
            "restype": c_bool,
        },
        {
            "name": "CH34x_GetDeviceID",
            "argtypes": (c_int32, POINTER(c_uint32)),
            "restype": c_bool,
        },
        {"name": "CH34xSetParaMode", "argtypes": (c_int32, c_uint8), "restype": c_bool},
        {
            "name": "CH34xInitParallel",
            "argtypes": (c_int32, c_uint8),
            "restype": c_bool,
        },
        {
            "name": "CH34xSetTimeout",
            "argtypes": (c_int32, c_uint32, c_uint32),
            "restype": c_bool,
        },
        {"name": "CH34xSetStream", "argtypes": (c_int32, c_uint8), "restype": c_bool},
        {
            "name": "CH34xStreamSPIx",
            "argtypes": (
                c_int32,
                c_uint32,
                c_uint32,
                POINTER(c_uint8),
                POINTER(c_uint8),
            ),
            "restype": c_bool,
        },
    ]

    for func in funcs:
        if not getattr(dll, func["name"], None):
            name_alternative = re.sub(r"^CH341", "CH34x", func["name"])
            f = getattr(dll, name_alternative)
            setattr(dll, func["name"], f)  # set alias

        getattr(dll, func["name"]).argtypes = func["argtypes"]
        getattr(dll, func["name"]).restype = func["restype"]

    return dll
