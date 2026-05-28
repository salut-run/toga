from win32more.Microsoft.UI.Xaml.Controls import ProgressRing

from .base import SimpleProbe


class ActivityIndicatorProbe(SimpleProbe):
    native_class = ProgressRing

    def assert_spinner_is_hidden(self, value):
        assert (not self.native.IsActive or self.hidden) == value
