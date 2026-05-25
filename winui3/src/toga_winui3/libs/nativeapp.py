# The application startup routine is derived from XamlApplication in py-win32more.
#
# MIT License
#
# Copyright (c) 2022 Yukihiro Nakadaira
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from win32more import FAILED, WinError
from win32more.Microsoft.UI.Xaml import Application, Window
from win32more.Windows.Win32.System.Com import (
    COINIT_APARTMENTTHREADED,
    CoInitializeEx,
    CoUninitialize,
)
from win32more.winui3 import XamlApplication


class NativeApp(XamlApplication):
    """Native WinUI application host with Toga lifecycle integration."""

    _current = None

    def __init__(self):
        type(self)._current = self
        super().__init__()

    def CreateWindow(self):
        return Window()

    @classmethod
    def current(cls):
        return cls._current

    @classmethod
    def Start(cls):
        hr = CoInitializeEx(None, COINIT_APARTMENTTHREADED)
        if FAILED(hr):
            raise WinError(hr)

        try:
            Application.Start(lambda *_args: cls())
            if cls._current is not None:
                cls._current.OnExited()
                cls._current.Release()
                cls._current = None
        finally:
            CoUninitialize()
