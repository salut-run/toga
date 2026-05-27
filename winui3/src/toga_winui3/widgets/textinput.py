from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import TextBox
from win32more.Windows.System import VirtualKey

from toga.handlers import WeakrefCallable

from .base import Widget, native_text_alignment


class TextInput(Widget):
    def create(self):
        self.native = TextBox()
        self.native.AcceptsReturn = False
        self.native.TextChanged += WeakrefCallable(self.native_event_text_changed)
        self.native.GotFocus += WeakrefCallable(self.native_event_got_focus)
        self.native.LostFocus += WeakrefCallable(self.native_event_lost_focus)
        self.native.KeyDown += WeakrefCallable(self.native_event_key_down)
        self._is_valid = True
        self._ignore_text_changed_value = None
        self._focus_reported = False

    def get_readonly(self):
        return self.native.IsReadOnly

    def set_readonly(self, value):
        self.native.IsReadOnly = value

    def get_placeholder(self):
        return self.native.PlaceholderText

    def set_placeholder(self, value):
        self.native.PlaceholderText = value

    def get_value(self):
        return self.native.Text

    def set_value(self, value):
        if self.native.Text != value:
            self._ignore_text_changed_value = value
            self.native.Text = value
            self.interface._value_changed()

    def set_text_align(self, value):
        self.native.TextAlignment = native_text_alignment(value)

    def is_valid(self):
        return self._is_valid

    def clear_error(self):
        self._is_valid = True

    def set_error(self, error_message):
        self._is_valid = False

    def native_event_text_changed(self, sender, args):
        if self._ignore_text_changed_value == self.native.Text:
            self._ignore_text_changed_value = None
        else:
            self._ignore_text_changed_value = None
            self.interface._value_changed()

    def native_event_key_down(self, sender, args):
        if args.Key == VirtualKey.Enter:
            self.interface.on_confirm()
            args.Handled = True

    def focus(self):
        previous = None
        if self.container:
            previous = next(
                (
                    widget
                    for widget in self.container.widgets._widgets
                    if widget is not self
                    and hasattr(widget, "_report_focus")
                    and hasattr(widget.interface, "on_lose_focus")
                    and widget.has_focus
                ),
                None,
            )
        super().focus()
        if previous is not None:
            previous._report_focus(False)
        self._report_focus(True)

    def _report_focus(self, focused):
        if focused == self._focus_reported:
            return
        self._focus_reported = focused
        if focused:
            self.interface.on_gain_focus()
        else:
            self.interface.on_lose_focus()

    def native_event_got_focus(self, sender, args):
        self._report_focus(True)

    def native_event_lost_focus(self, sender, args):
        self._report_focus(False)

    def rehint(self):
        desired_size = self.measure_unconstrained()
        self.interface.intrinsic.width = at_least(
            max(self.interface._MIN_WIDTH, desired_size.Width)
        )
        self.interface.intrinsic.height = max(
            desired_size.Height,
            self.native.FontSize + 18,
        )
