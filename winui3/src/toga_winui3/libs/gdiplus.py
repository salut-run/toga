from contextlib import contextmanager
from ctypes import WinError, byref

from win32more.Windows.Win32.Foundation import BOOL, UIntPtr
from win32more.Windows.Win32.Graphics.GdiPlus import (
    GdiplusShutdown,
    GdiplusStartup,
    GdiplusStartupInput,
    GdiplusStartupOutput,
)

status_dict = {
    0: "Ok",
    1: "GenericError",
    2: "InvalidParameter",
    3: "OutOfMemory",
    4: "ObjectBusy",
    5: "InsufficientBuffer",
    6: "NotImplemented",
    7: "Win32Error",
    8: "WrongState",
    9: "Aborted",
    10: "FileNotFound",
    11: "ValueOverflow",
    12: "AccessDenied",
    13: "UnknownImageFormat",
    14: "FontFamilyNotFound",
    15: "FontStyleNotFound",
    16: "NotTrueTypeFont",
    17: "UnsupportedGdiplusVersion",
    18: "GdiplusNotInitialized",
    19: "PropertyNotFound",
    20: "PropertyNotSupported",
    21: "ProfileNotFound",
}


@contextmanager
def gdi_plus():
    """Start GDI+ for the duration of a native image operation."""
    startup_input = GdiplusStartupInput()
    startup_input.GdiplusVersion = 1
    startup_input.DebugEventCallback = 0
    startup_input.SuppressBackgroundThread = BOOL(0)
    startup_input.SuppressExternalCodecs = BOOL(0)

    token = UIntPtr()
    output = GdiplusStartupOutput()
    status = GdiplusStartup(byref(token), byref(startup_input), byref(output))
    if status != 0:
        raise WinError(descr=f"GdiplusStartup failed with code: {status_dict[status]}")

    try:
        yield
    finally:
        GdiplusShutdown(token)
