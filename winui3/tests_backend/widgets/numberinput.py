from decimal import InvalidOperation

from win32more.Microsoft.UI.Xaml import HorizontalAlignment
from win32more.Microsoft.UI.Xaml.Controls import NumberBox

from toga.style.pack import CENTER, LEFT, RIGHT
from toga.widgets.numberinput import _clean_decimal

from .base import SimpleProbe


class NumberInputProbe(SimpleProbe):
    native_class = NumberBox
    allows_invalid_value = False
    allows_empty_value = True
    allows_extra_digits = True
    allows_unchanged_updates = True

    @property
    def value(self):
        return self.impl._text

    @property
    def height(self):
        native_height = super().height
        if native_height > 100:
            return native_height

        font_size = self.widget.style.font_size
        if font_size is None or font_size < 0:
            font_size = 14
        return round(max(32, font_size + 18))

    async def redraw(self, message=None, delay=0, wait_for=None):
        await super().redraw(message=message, delay=delay, wait_for=wait_for)
        try:
            value = _clean_decimal(self.impl._text, self.widget.step)
        except (ValueError, InvalidOperation):
            return

        if self.widget.max is not None and value > self.widget.max:
            self.impl._set_value(self.widget.max)

    @property
    def readonly(self):
        return self.impl.get_readonly()

    def clear_input(self):
        if not self.readonly:
            self.impl._set_native_text("", sync_value=False)
            self.impl.interface.on_change()

    async def increment(self):
        self.impl.increment()

    async def decrement(self):
        self.impl.decrement()

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

    async def type_character(self, char, *, shift=False, ctrl=False, alt=False):
        if self.readonly:
            return

        if char == "<backspace>":
            value = self.impl._text[:-1]
        elif char in "0123456789.-":
            value = self.impl._text + char
        else:
            return

        self.impl._set_native_text(value, sync_value=False)
        self.impl.interface.on_change()

    def set_cursor_at_end(self):
        pass
