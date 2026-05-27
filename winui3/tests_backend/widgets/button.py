import pytest
from win32more.Microsoft.UI.Xaml.Controls import Button as NativeButton

from .base import SimpleProbe


class ButtonProbe(SimpleProbe):
    native_class = NativeButton

    @property
    def text(self):
        return self.native.Content if isinstance(self.native.Content, str) else ""

    def assert_no_icon(self):
        assert isinstance(self.native.Content, str)

    def assert_icon_size(self):
        pytest.skip("WinUI 3 button icon probing is not implemented yet.")
