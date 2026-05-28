from pytest import approx
from win32more.Microsoft.UI.Windowing import DisplayArea

from toga.images import Image as TogaImage

from .probe import BaseProbe


class ScreenProbe(BaseProbe):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self._impl = screen._impl
        self.native = screen._impl.native
        assert isinstance(self.native, DisplayArea)

    def get_screenshot(self, format=TogaImage):
        return self.screen.as_image(format=format)

    def assert_dpi_scaling(self):
        native_bounds = self.native.OuterBounds
        screen_size = self.screen.size

        assert self._impl.dpi_scale > 0
        assert self._impl.pixels_to_css(native_bounds.Width) == screen_size[0]
        assert self._impl.pixels_to_css(native_bounds.Height) == screen_size[1]
        assert self._impl.pixels_to_physical(screen_size[0]) == approx(
            native_bounds.Width,
            abs=1,
        )
        assert self._impl.pixels_to_physical(screen_size[1]) == approx(
            native_bounds.Height,
            abs=1,
        )
