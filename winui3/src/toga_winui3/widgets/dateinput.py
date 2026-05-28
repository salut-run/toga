from datetime import date, datetime, timedelta

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import DatePicker
from win32more.Windows.Foundation import DateTime

from toga.handlers import WeakrefCallable
from toga.widgets.dateinput import MAX_DATE, MIN_DATE

from .base import Widget

TICKS_PER_SECOND = 10_000_000
WINDOWS_EPOCH = datetime(1601, 1, 1)


def py_date(native_date):
    return (
        WINDOWS_EPOCH + timedelta(microseconds=native_date.UniversalTime // 10)
    ).date()


def native_date(py_date):
    delta = datetime(py_date.year, py_date.month, py_date.day) - WINDOWS_EPOCH
    return DateTime(
        ((delta.days * 24 * 60 * 60) + delta.seconds) * TICKS_PER_SECOND
        + (delta.microseconds * 10)
    )


class DateInput(Widget):
    def create(self):
        self.native = DatePicker()
        self.native.MinYear = native_date(MIN_DATE)
        self.native.MaxYear = native_date(MAX_DATE)
        self.native.Date = native_date(date.today())
        self.native.DateChanged += WeakrefCallable(self.native_event_date_changed)

    def get_value(self):
        return py_date(self.native.Date)

    def set_value(self, value):
        self.native.Date = native_date(value)

    def get_min_date(self):
        return py_date(self.native.MinYear)

    def set_min_date(self, value):
        self.native.MinYear = native_date(value)

    def get_max_date(self):
        return py_date(self.native.MaxYear)

    def set_max_date(self, value):
        self.native.MaxYear = native_date(value)

    def native_event_date_changed(self, sender, args):
        self.interface.on_change()

    def rehint(self):
        desired_size = self.measure_unconstrained()
        self.interface.intrinsic.width = at_least(
            max(self.interface._MIN_WIDTH, desired_size.Width)
        )
        self.interface.intrinsic.height = desired_size.Height
