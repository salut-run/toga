from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import Border

from toga.colors import rgb

from ..colors import native_brush
from .base import Widget


class Divider(Widget):
    THICKNESS = 1

    def create(self):
        self.native = Border()
        self.native.Background = native_brush(rgb(160, 160, 160))
        self._direction = self.interface.HORIZONTAL

    def set_background_color(self, value):
        pass

    def get_direction(self):
        return self._direction

    def set_direction(self, value):
        self._direction = (
            self.interface.VERTICAL
            if value == self.interface.VERTICAL
            else self.interface.HORIZONTAL
        )

    def rehint(self):
        if self.get_direction() == self.interface.VERTICAL:
            self.interface.intrinsic.width = self.THICKNESS
            self.interface.intrinsic.height = at_least(0)
        else:
            self.interface.intrinsic.width = at_least(0)
            self.interface.intrinsic.height = self.THICKNESS
