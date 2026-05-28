from win32more.Microsoft.UI.Xaml import Visibility
from win32more.Microsoft.UI.Xaml.Controls import ProgressRing

from .base import Widget


class ActivityIndicator(Widget):
    SPINNER_SIZE = 32

    def create(self):
        self.native = ProgressRing()
        self.native.IsIndeterminate = True
        self.native.IsActive = False
        self.native.IsTabStop = False

        self._hidden = False
        self._running = False
        self._update_visibility()

    def _update_visibility(self):
        self.native.Visibility = (
            Visibility.Visible
            if self._running and not self._hidden
            else Visibility.Collapsed
        )

    def set_hidden(self, hidden):
        self._hidden = hidden
        self._update_visibility()

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def has_focus(self):
        return False

    def focus(self):
        pass

    def is_running(self):
        return self._running

    def start(self):
        self._running = True
        self.native.IsActive = True
        self._update_visibility()

    def stop(self):
        self._running = False
        self.native.IsActive = False
        self._update_visibility()

    def rehint(self):
        self.interface.intrinsic.width = self.SPINNER_SIZE
        self.interface.intrinsic.height = self.SPINNER_SIZE
