from datetime import time

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import TimePicker
from win32more.Windows.Foundation import TimeSpan

from toga.handlers import WeakrefCallable

from .base import Widget
from .dateinput import TICKS_PER_SECOND


def py_time(native_time):
    total_seconds = native_time.Duration // TICKS_PER_SECOND
    return time(
        total_seconds // 3600,
        (total_seconds // 60) % 60,
        total_seconds % 60,
    )


def native_time(py_time):
    return TimeSpan(
        ((py_time.hour * 60 * 60) + (py_time.minute * 60) + py_time.second)
        * TICKS_PER_SECOND
    )


def normalize_time(py_time):
    return py_time.replace(second=0)


class TimeInput(Widget):
    def create(self):
        self.native = TimePicker()
        self.native.Time = native_time(time(0, 0, 0))
        self.native.TimeChanged += WeakrefCallable(self.native_event_time_changed)
        self._min_time = time(0, 0, 0)
        self._max_time = time(23, 59, 0)

    def get_value(self):
        return py_time(self.native.Time)

    def set_value(self, value):
        self.native.Time = native_time(normalize_time(value))

    def get_min_time(self):
        return self._min_time

    def set_min_time(self, value):
        self._min_time = normalize_time(value)

    def get_max_time(self):
        return self._max_time

    def set_max_time(self, value):
        self._max_time = normalize_time(value)

    def native_event_time_changed(self, sender, args):
        value = self.get_value()
        if value < self._min_time:
            self.set_value(self._min_time)
        elif value > self._max_time:
            self.set_value(self._max_time)
        else:
            self.interface.on_change()

    def rehint(self):
        desired_size = self.measure_unconstrained()
        self.interface.intrinsic.width = at_least(
            max(self.interface._MIN_WIDTH, desired_size.Width)
        )
        self.interface.intrinsic.height = desired_size.Height
