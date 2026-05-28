from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import Slider as NativeSlider
from win32more.Microsoft.UI.Xaml.Controls.Primitives import (
    SliderSnapsTo,
    TickPlacement,
)

from toga.handlers import WeakrefCallable
from toga.widgets.slider import SliderImpl

from .base import Widget


class Slider(Widget, SliderImpl):
    def create(self):
        self.native = NativeSlider()
        self.native.ValueChanged += WeakrefCallable(self.native_event_value_changed)
        self.native.PointerPressed += WeakrefCallable(self.native_event_pointer_pressed)
        self.native.PointerReleased += WeakrefCallable(
            self.native_event_pointer_released
        )
        self._tick_count = None

    def native_event_value_changed(self, sender, args):
        self.interface.on_change()

    def native_event_pointer_pressed(self, sender, args):
        self.interface.on_press()

    def native_event_pointer_released(self, sender, args):
        self.interface.on_release()

    def get_value(self):
        return self.native.Value

    def set_value(self, value):
        self.native.Value = value

    def get_min(self):
        return self.native.Minimum

    def set_min(self, value):
        self.native.Minimum = value
        self._update_tick_frequency()

    def get_max(self):
        return self.native.Maximum

    def set_max(self, value):
        self.native.Maximum = value
        self._update_tick_frequency()

    def get_tick_count(self):
        return self._tick_count

    def set_tick_count(self, tick_count):
        self._tick_count = tick_count
        self.native.TickPlacement = (
            TickPlacement.BottomRight if tick_count is not None else TickPlacement.None_
        )
        self.native.SnapsTo = (
            SliderSnapsTo.Ticks if tick_count is not None else SliderSnapsTo.StepValues
        )
        self._update_tick_frequency()

    def _update_tick_frequency(self):
        if self._tick_count is None:
            self.native.StepFrequency = 0
            self.native.TickFrequency = 0
        else:
            self.native.StepFrequency = self.native.TickFrequency = (
                0
                if self._tick_count < 2
                else (self.native.Maximum - self.native.Minimum)
                / (self._tick_count - 1)
            )

    def rehint(self):
        desired_size = self.measure_unconstrained()
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = desired_size.Height
