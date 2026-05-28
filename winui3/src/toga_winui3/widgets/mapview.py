from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import Grid, TextBlock

import toga

from .base import Widget


class MapView(Widget):
    SUPPORTS_ON_SELECT = True

    def create(self):
        self.native = Grid()
        self.native.IsTabStop = True
        self.placeholder = TextBlock()
        self.placeholder.Text = "MapView"
        self.native.Children.Append(self.placeholder)

        self.backlog = None
        self._location = toga.LatLng(-31.9559, 115.8606)
        self._zoom = 11
        self._pins = set()

    def get_location(self):
        return self._location

    def set_location(self, position):
        self._location = toga.LatLng(*position)

    def get_zoom(self):
        return self._zoom

    def set_zoom(self, zoom):
        self._zoom = zoom

    def tile_longitude_span(self):
        return 360 / (2**self._zoom)

    def add_pin(self, pin):
        pin._native = pin
        self._pins.add(pin)

    def update_pin(self, pin):
        pass

    def remove_pin(self, pin):
        self._pins.remove(pin)
        pin._native = None

    @property
    def pin_count(self):
        return len(self._pins)

    def select_pin(self, pin):
        self.interface.on_select(pin=pin)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
