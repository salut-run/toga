from travertino.size import at_least
from win32more.Microsoft.UI.Xaml import TextWrapping
from win32more.Microsoft.UI.Xaml.Controls import ScrollViewer, TextBox
from win32more.Microsoft.UI.Xaml.Media import VisualTreeHelper

from toga.handlers import WeakrefCallable

from .base import Widget
from .textinput import TextInput


class MultilineTextInput(TextInput):
    def create(self):
        self.native = TextBox()
        self.native.AcceptsReturn = True
        self.native.TextWrapping = TextWrapping.Wrap
        self.native.TextChanged += WeakrefCallable(self.native_event_text_changed)
        self._ignore_text_changed_value = None
        self._native_scroll_viewer = None

    def _normalize_value(self, value):
        return value.replace("\r\n", "\n").replace("\r", "\n")

    def get_value(self):
        return self._normalize_value(self.native.Text)

    def set_value(self, value):
        if self.get_value() != value:
            self._ignore_text_changed_value = self._normalize_value(value)
            self.native.Text = value
            self.interface.on_change()

    def native_event_text_changed(self, sender, args):
        value = self.get_value()
        if self._ignore_text_changed_value == value:
            self._ignore_text_changed_value = None
        else:
            self._ignore_text_changed_value = None
            self.interface.on_change()

    def scroll_to_bottom(self):
        if scroll_viewer := self._scroll_viewer:
            scroll_viewer.ScrollToVerticalOffset(scroll_viewer.ScrollableHeight)
        else:
            self.native.Select(len(self.native.Text), 0)

    def scroll_to_top(self):
        if scroll_viewer := self._scroll_viewer:
            scroll_viewer.ScrollToVerticalOffset(0)
        else:
            self.native.Select(0, 0)

    def focus(self):
        Widget.focus(self)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)

    @property
    def _scroll_viewer(self):
        if self._native_scroll_viewer is None:
            self.native.UpdateLayout()
            self._native_scroll_viewer = self._find_scroll_viewer(self.native)

        return self._native_scroll_viewer

    def _find_scroll_viewer(self, native):
        child_count = VisualTreeHelper.GetChildrenCount(native)
        for index in range(child_count):
            child = VisualTreeHelper.GetChild(native, index)
            try:
                return child.as_(ScrollViewer)
            except (AttributeError, OSError, TypeError):
                if scroll_viewer := self._find_scroll_viewer(child):
                    return scroll_viewer

        return None
