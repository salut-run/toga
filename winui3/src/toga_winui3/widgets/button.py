from travertino.constants import TRANSPARENT
from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import (
    Button as NativeButton,
    Control,
    Image as NativeImage,
    TextBlock,
)
from win32more.Microsoft.UI.Xaml.Media import Stretch

from toga.handlers import WeakrefCallable

from .base import Widget, WidgetStager


class Button(Widget):
    def create(self):
        self.native = NativeButton()
        self._constraints = WidgetStager(self)
        self._icon = None
        self._text = ""

        self.native.Click += WeakrefCallable(self.native_event_click)

    def native_event_click(self, sender, args):
        self.interface.on_press()

    def set_background_color(self, color):
        if color == TRANSPARENT:
            self.native.ClearValue(Control.BackgroundProperty)
        else:
            super().set_background_color(color)

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

        if self._icon is not None:
            return

        def creator(text=text):
            text_block = TextBlock()
            # "\u200b" (ZERO WIDTH SPACE) instead of "" ensures correct button height.
            text_block.Text = "\u200b" if text == "" else text
            return text_block

        self.content_creator = creator

    def get_icon(self):
        return self._icon

    def set_icon(self, icon):
        self._icon = icon

        if icon is None:
            return

        def creator(icon=icon):
            image = NativeImage()
            image.Width = 32
            image.Height = 32
            image.Stretch = Stretch.Uniform
            image.Source = icon._impl.bitmap_image(32)
            return image

        self.content_creator = creator

    def rehint(self):
        self.interface.intrinsic.width = at_least(self._constraints.width)
        self.interface.intrinsic.height = self._constraints.height
