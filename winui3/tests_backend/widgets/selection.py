from pytest import xfail
from win32more.Microsoft.UI.Xaml.Controls import ComboBox

from .base import SimpleProbe


def int_value(value):
    return int(getattr(value, "value", value))


class SelectionProbe(SimpleProbe):
    native_class = ComboBox

    def assert_resizes_on_content_change(self):
        pass

    @property
    def text_align(self):
        xfail("Can't change the text alignment of Selection on WinUI")

    def assert_vertical_text_align(self, expected):
        pass

    @property
    def titles(self):
        return list(self.impl._item_titles)

    @property
    def selected_title(self):
        index = int_value(self.native.SelectedIndex)
        if index == -1:
            return None
        return self.titles[index]

    async def select_item(self):
        self.native.SelectedIndex = 1
