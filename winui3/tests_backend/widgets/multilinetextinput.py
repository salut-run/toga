from win32more.Microsoft.UI.Xaml.Controls import TextBox

from .textinput import TextInputProbe


class MultilineTextInputProbe(TextInputProbe):
    native_class = TextBox
    supports_simulate_mouse_wheel = False

    @property
    def value(self):
        if self.placeholder_visible:
            return self.native.PlaceholderText
        return self.impl.get_value()

    def _char_rect(self, index, trailing_edge=False):
        return self.native.GetRectFromCharacterIndex(index, trailing_edge)

    @property
    def document_width(self):
        return self.width

    @property
    def document_height(self):
        if scroll_viewer := self.impl._scroll_viewer:
            if scroll_viewer.ExtentHeight:
                return round(scroll_viewer.ExtentHeight)

        text_length = len(self.native.Text)
        line_height = max(round(self.native.FontSize + 8), 1)
        if text_length == 0:
            return line_height

        start = self._char_rect(0)
        end = self._char_rect(text_length - 1, True)
        return round((end.Y - start.Y) + max(end.Height, line_height))

    @property
    def vertical_scroll_position(self):
        if scroll_viewer := self.impl._scroll_viewer:
            return round(scroll_viewer.VerticalOffset)

        if len(self.native.Text) == 0:
            return 0

        return max(0, -round(self._char_rect(0).Y))

    async def wait_for_scroll_completion(self):
        pass

    async def type_character(self, char, *, shift=False, ctrl=False, alt=False):
        if char == "<esc>" or self.native.IsReadOnly:
            return

        start = self.native.SelectionStart
        length = self.native.SelectionLength
        text = self.native.Text
        value = text[:start] + char + text[start + length :]
        self.impl._ignore_text_changed_value = self.impl._normalize_value(value)
        self.native.Text = value
        self.native.SelectionStart = start + len(char)
        self.native.SelectionLength = 0
        self.impl.interface.on_change()
