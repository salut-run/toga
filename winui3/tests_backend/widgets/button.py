import pytest
from win32more.Microsoft.UI.Xaml.Controls import (
    Button as NativeButton,
    Image as NativeImage,
    TextBlock,
)

from .base import SimpleProbe


class ButtonProbe(SimpleProbe):
    native_class = NativeButton

    @property
    def font_target(self):
        return self.native.Content.as_(TextBlock)

    @property
    def text(self):
        try:
            text = self.native.Content.as_(TextBlock).Text
        except (AttributeError, OSError, TypeError):
            try:
                text = self.native.Content.as_(str)
            except (AttributeError, OSError, TypeError):
                text = ""

        # Normalize the zero width space to the empty string.
        if text == "\u200b":
            return ""
        return text

    def assert_no_icon(self):
        assert self.native.Content.as_(TextBlock) is not None

    def assert_icon_size(self):
        try:
            icon = self.native.Content.as_(NativeImage)
        except (AttributeError, OSError, TypeError):
            pytest.fail("Icon does not exist")

        assert (icon.Width, icon.Height) == (32, 32)
