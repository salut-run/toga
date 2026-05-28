from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import ProgressBar as WinUIProgressBar

from .base import Widget


class ProgressBar(Widget):
    def create(self):
        self.native = WinUIProgressBar()
        self.native.Minimum = 0
        self.native.Maximum = 1
        self.native.Value = 0
        self.native.IsIndeterminate = False
        self.native.IsTabStop = True

        self._running = False
        self._max = 1.0

    def is_running(self):
        return self._running

    def start(self):
        self._running = True
        self._update_native_mode()

    def stop(self):
        self._running = False
        self._update_native_mode()

    def get_max(self):
        return self._max

    def set_max(self, value):
        if value is None:
            self._max = None
            self.native.Value = 0
        else:
            if self._max is None:
                self.native.Value = 0

            self._max = value
            self.native.Minimum = 0
            self.native.Maximum = value

        self._update_native_mode()

    def get_value(self):
        if self._max is None:
            return None

        return self.native.Value

    def set_value(self, value):
        self.native.Value = value

    def _update_native_mode(self):
        self.native.IsIndeterminate = self._running and self._max is None

    def rehint(self):
        desired_size = self.measure_unconstrained()
        self.interface.intrinsic.width = at_least(
            max(self.interface._MIN_WIDTH, desired_size.Width)
        )
        self.interface.intrinsic.height = desired_size.Height
