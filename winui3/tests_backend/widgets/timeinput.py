from datetime import date, datetime, timedelta

from win32more.Microsoft.UI.Xaml.Controls import TimePicker

from toga_winui3.widgets.timeinput import native_time, py_time

from .base import SimpleProbe


class TimeInputProbe(SimpleProbe):
    native_class = TimePicker
    supports_limits = False
    supports_seconds = False

    @property
    def value(self):
        return py_time(self.native.Time)

    async def change(self, delta):
        value = (
            datetime.combine(date.today(), self.value) + timedelta(minutes=delta)
        ).time()
        if self.impl.get_min_time() <= value <= self.impl.get_max_time():
            self.native.Time = native_time(value)
        await self.redraw(f"Change value by {delta} minutes")
