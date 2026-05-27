import math
import sys
from decimal import InvalidOperation

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import (
    NumberBox,
    NumberBoxSpinButtonPlacementMode,
    NumberBoxValidationMode,
)

from toga.handlers import WeakrefCallable
from toga.widgets.numberinput import _clean_decimal

from .base import Widget, native_horizontal_alignment


class NumberInput(Widget):
    def create(self):
        self.native = NumberBox()
        self.native.MinWidth = 0
        self.native.AllowFocusOnInteraction = True
        self.native.IsTabStop = True
        self.native.SpinButtonPlacementMode = NumberBoxSpinButtonPlacementMode.Inline
        self.native.ValidationMode = NumberBoxValidationMode.Disabled
        self.native.ValueChanged += WeakrefCallable(self.native_event_value_changed)
        self._text = ""
        self._readonly = False
        self._send_notifications = True

    def native_event_value_changed(self, sender, args):
        if self._send_notifications:
            self._text = self.native.Text
            self.interface.on_change()

    def _with_notifications_suspended(self, callback):
        self._send_notifications = False
        try:
            callback()
        finally:
            self._send_notifications = True

    def _set_native_text(self, text, *, sync_value=True):
        def setter():
            self._text = text
            self.native.Text = text
            if sync_value:
                try:
                    self.native.Value = float(_clean_decimal(text, self.interface.step))
                except (ValueError, InvalidOperation):
                    self.native.Value = math.nan

        self._with_notifications_suspended(setter)

    def _set_value(self, value):
        if value is None:
            self._set_native_text("")
        else:
            self._set_native_text(str(value))

    def get_readonly(self):
        return self._readonly

    def set_readonly(self, value):
        self._readonly = bool(value)

    def set_step(self, step):
        self.native.SmallChange = float(step)
        self.native.LargeChange = float(step)

    def set_min_value(self, value):
        self.native.Minimum = -sys.float_info.max if value is None else float(value)

    def set_max_value(self, value):
        self.native.Maximum = sys.float_info.max if value is None else float(value)

    def get_value(self):
        try:
            return _clean_decimal(self._text, self.interface.step)
        except (ValueError, InvalidOperation):
            return None

    def set_value(self, value):
        old_value = self.get_value()
        self._set_value(value)
        if self.get_value() != old_value:
            self.interface.on_change()

    def set_text_align(self, value):
        super().set_text_align(value)
        self.native.HorizontalContentAlignment = native_horizontal_alignment(value)

    def increment(self):
        value = self.interface.value
        if value is None:
            value = 0
        self.interface.value = value + self.interface.step

    def decrement(self):
        value = self.interface.value
        if value is None:
            value = 0
        self.interface.value = value - self.interface.step

    def rehint(self):
        desired_size = self.measure_unconstrained()
        height = desired_size.Height
        if hasattr(self, "_font"):
            height = max(height, self.native.FontSize + 18)

        self.interface.intrinsic.width = at_least(
            max(self.interface._MIN_WIDTH, desired_size.Width)
        )
        self.interface.intrinsic.height = height
