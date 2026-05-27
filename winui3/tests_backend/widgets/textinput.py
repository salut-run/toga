from win32more.Microsoft.UI.Xaml import TextAlignment
from win32more.Microsoft.UI.Xaml.Controls import TextBox
from win32more.Windows.System import VirtualKey

from toga.style.pack import CENTER, JUSTIFY, LEFT, RIGHT

from .base import SimpleProbe


class KeyEventArgs:
    def __init__(self, key):
        self.Key = key
        self.Handled = False


class TextInputProbe(SimpleProbe):
    native_class = TextBox
    redo_available = False

    @property
    def value(self):
        if self.placeholder_visible:
            return self.native.PlaceholderText
        return self.native.Text

    @property
    def value_hidden(self):
        return False

    @property
    def readonly(self):
        return self.native.IsReadOnly

    @property
    def text_align(self):
        return {
            TextAlignment.Left: LEFT,
            TextAlignment.Center: CENTER,
            TextAlignment.Right: RIGHT,
            TextAlignment.Justify: JUSTIFY,
        }[self.native.TextAlignment]

    def assert_vertical_text_align(self, expected):
        pass

    @property
    def placeholder_visible(self):
        return self.native.Text == "" and self.native.PlaceholderText != ""

    @property
    def placeholder_hides_on_focus(self):
        return False

    async def type_character(self, char, *, shift=False, ctrl=False, alt=False):
        if char == "\n":
            self.impl.native_event_key_down(None, KeyEventArgs(VirtualKey.Enter))
            return

        if char == "<esc>" or self.native.IsReadOnly:
            return

        start = self.native.SelectionStart
        length = self.native.SelectionLength
        text = self.native.Text
        value = text[:start] + char + text[start + length :]
        self.impl._ignore_text_changed_value = value
        self.native.Text = value
        self.native.SelectionStart = start + len(char)
        self.native.SelectionLength = 0
        self.impl.interface._value_changed()

    def set_cursor_at_end(self):
        self.native.SelectionStart = len(self.native.Text)
        self.native.SelectionLength = 0

    def select_range(self, start, length):
        self.native.SelectionStart = start
        self.native.SelectionLength = length
