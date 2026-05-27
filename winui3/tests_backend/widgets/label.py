from win32more.Microsoft.UI.Xaml import TextAlignment
from win32more.Microsoft.UI.Xaml.Controls import Border

from toga.style.pack import CENTER, JUSTIFY, LEFT, RIGHT

from .base import SimpleProbe, toga_color


class LabelProbe(SimpleProbe):
    native_class = Border

    @property
    def font_target(self):
        return self.impl.textblock

    @property
    def text(self):
        if self.impl.textblock.Text == "\u200b":
            return ""
        return self.impl.textblock.Text

    @property
    def color(self):
        return toga_color(self.impl.textblock.Foreground)

    @property
    def text_align(self):
        return {
            TextAlignment.Left: LEFT,
            TextAlignment.Center: CENTER,
            TextAlignment.Right: RIGHT,
            TextAlignment.Justify: JUSTIFY,
        }[self.impl.textblock.TextAlignment]

    def assert_vertical_text_align(self, expected):
        pass
