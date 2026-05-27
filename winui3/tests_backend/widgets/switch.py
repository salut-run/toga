from win32more.Microsoft.UI.Xaml.Controls import StackPanel

from .base import SimpleProbe, toga_color


class SwitchProbe(SimpleProbe):
    native_class = StackPanel

    @property
    def font_target(self):
        return self.impl.native_label

    @property
    def text(self):
        text = self.impl.native_label.Text
        if text == "\u200b":
            return ""
        return text

    @property
    def color(self):
        return toga_color(self.impl.native_label.Foreground)

    async def press(self):
        self.impl.set_value(not self.impl.get_value())
