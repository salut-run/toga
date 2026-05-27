from travertino.size import at_least
from win32more.Microsoft.UI.Xaml import ThicknessHelper, VerticalAlignment
from win32more.Microsoft.UI.Xaml.Controls import (
    Orientation,
    StackPanel,
    TextBlock,
    ToggleSwitch,
)

from toga.handlers import WeakrefCallable

from ..colors import native_brush
from .base import Widget, WidgetStager


class Switch(Widget):
    def create(self):
        self.native = StackPanel()
        self.native.Orientation = Orientation.Horizontal

        self.native_label = TextBlock()
        self.native_label.VerticalAlignment = VerticalAlignment.Center
        self.native.Children.Append(self.native_label)

        self.native_toggle = ToggleSwitch()
        self.native_toggle.MinWidth = 0
        self.native_toggle.OnContent = ""
        self.native_toggle.OffContent = ""
        self.native_toggle.VerticalAlignment = VerticalAlignment.Center
        self.native.Children.Append(self.native_toggle)
        self._constraints = WidgetStager(self)
        self._text = ""
        self._setting_value = False
        self.native_toggle.Toggled += WeakrefCallable(self.native_event_checked_changed)

    def native_event_checked_changed(self, sender, args):
        if not self._setting_value:
            self.interface.on_change()

    def get_enabled(self):
        return self.native_toggle.IsEnabled

    def set_enabled(self, value):
        self.native_toggle.IsEnabled = value
        self.native_label.Opacity = 1 if value else 0.5

    @property
    def _focus_target(self):
        return self.native_toggle

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text

        def creator(text=text):
            return text

        self.content_creator = creator

    def set_color(self, color):
        if color is None:
            self.native_label.ClearValue(TextBlock.ForegroundProperty)
        else:
            self.native_label.Foreground = native_brush(color)

    def set_font(self, font):
        self._font = font
        self._apply_font(self.native_label)
        self.native_label.MinHeight = font._impl.native_size + 18

        if self._container:
            self._constraints.refresh()

    def set_native_content(self, content):
        self.content = content
        self.native_label.Text = "\u200b" if content == "" else content
        self.native_label.Margin = ThicknessHelper.FromLengths(
            0,
            0,
            8 if content else 0,
            0,
        )
        if hasattr(self, "_font"):
            self._apply_font(self.native_label)
            self.native_label.MinHeight = self._font._impl.native_size + 18

    def get_value(self):
        return bool(self.native_toggle.IsOn)

    def set_value(self, value):
        value = bool(value)
        old_value = self.get_value()
        if value != old_value:
            self._setting_value = True
            try:
                self.native_toggle.IsOn = value
            finally:
                self._setting_value = False
            self.interface.on_change()

    def rehint(self):
        self.interface.intrinsic.width = at_least(self._constraints.width)
        self.interface.intrinsic.height = self._constraints.height
