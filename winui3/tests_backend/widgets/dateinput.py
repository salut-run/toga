from datetime import timedelta

from win32more.Microsoft.UI.Xaml.Controls import DatePicker

from toga_winui3.widgets.dateinput import native_date, py_date

from .base import SimpleProbe


class DateInputProbe(SimpleProbe):
    native_class = DatePicker
    supports_limits = True

    @property
    def value(self):
        return py_date(self.native.Date)

    @property
    def min_value(self):
        return py_date(self.native.MinYear)

    @property
    def max_value(self):
        return py_date(self.native.MaxYear)

    async def change(self, delta):
        value = self.value + timedelta(days=delta)
        if self.min_value <= value <= self.max_value:
            self.native.Date = native_date(value)
        await self.redraw(f"Change value by {delta} days")
