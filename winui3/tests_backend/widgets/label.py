from win32more.Microsoft.UI.Xaml.Controls import TextBlock

from .base import SimpleProbe


class LabelProbe(SimpleProbe):
    native_class = TextBlock

    @property
    def text(self):
        return self.native.Text
