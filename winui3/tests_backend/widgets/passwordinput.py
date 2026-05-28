from win32more.Microsoft.UI.Xaml import HorizontalAlignment
from win32more.Microsoft.UI.Xaml.Controls import PasswordBox
from win32more.Windows.System import VirtualKey

from toga.style.pack import CENTER, LEFT, RIGHT

from .base import SimpleProbe
from .textinput import KeyEventArgs


class PasswordInputProbe(SimpleProbe):
    native_class = PasswordBox
    redo_available = False

    @property
    def value(self):
        if self.placeholder_visible:
            return self.native.PlaceholderText
        return self.native.Password

    @property
    def value_hidden(self):
        return True

    @property
    def readonly(self):
        return self.impl.get_readonly()

    @property
    def text_align(self):
        return {
            HorizontalAlignment.Left: LEFT,
            HorizontalAlignment.Center: CENTER,
            HorizontalAlignment.Right: RIGHT,
            HorizontalAlignment.Stretch: LEFT,
        }[self.native.HorizontalContentAlignment]

    def assert_vertical_text_align(self, expected):
        pass

    @property
    def placeholder_visible(self):
        return self.native.Password == "" and self.native.PlaceholderText != ""

    @property
    def placeholder_hides_on_focus(self):
        return False

    async def type_character(self, char, *, shift=False, ctrl=False, alt=False):
        if char == "\n":
            self.impl.native_event_key_down(None, KeyEventArgs(VirtualKey.Enter))
            return

        if char == "<esc>" or self.impl.get_readonly():
            return

        value = self.native.Password + char
        self.impl._ignore_password_changed_value = value
        self.native.Password = value
        self.impl._previous_password = value
        self.impl.interface._value_changed()

    def set_cursor_at_end(self):
        pass

    def select_range(self, start, length):
        pass
