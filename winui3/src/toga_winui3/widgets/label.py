from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import Border, TextBlock

from ..colors import native_brush
from .base import Widget, WidgetStager, native_text_alignment


class Label(Widget):
    def create(self):
        self.native = Border()
        self.textblock = TextBlock()
        self.native.Child = self.textblock
        self._constraints = WidgetStager(self)
        self._text = ""
        self._enabled = True

    def set_text_align(self, value):
        self.textblock.TextAlignment = native_text_alignment(value)

    def get_enabled(self):
        return self._enabled

    def set_enabled(self, value):
        self._enabled = value
        self.native.Opacity = 1 if value else 0.5

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

        def creator(text=text):
            return text

        self.content_creator = creator

    def set_background_color(self, color):
        if color is None:
            self.native.ClearValue(Border.BackgroundProperty)
        else:
            self.native.Background = native_brush(color)

    def set_color(self, color):
        if color is None:
            self.textblock.ClearValue(TextBlock.ForegroundProperty)
        else:
            self.textblock.Foreground = native_brush(color)

    def set_font(self, font):
        self._font = font
        self._apply_font(self.textblock)

        self._constraints.invalidate()
        if self._container:
            self._constraints.refresh()

    def set_native_content(self, content):
        self.content = content
        self.textblock.Text = "\u200b" if content == "" else content
        if hasattr(self, "_font"):
            self._apply_font(self.textblock)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self._constraints.width)
        self.interface.intrinsic.height = self._constraints.height
