import asyncio
from math import isfinite

from pytest import approx

from .fonts import FontMixin


class BaseProbe(FontMixin):
    fixed_height = None

    def __init__(self, native=None):
        self.native = native

    async def redraw(self, message=None, delay=0, wait_for=None):
        if delay or wait_for:
            if wait_for is None:
                await asyncio.sleep(delay)
            else:
                delta = 0.1
                interval = 0.0
                while not wait_for() and interval < delay:
                    await asyncio.sleep(delta)
                    interval += delta
        else:
            await asyncio.sleep(0)

    @property
    def x(self):
        return round(self.native.ActualOffset.X)

    @property
    def y(self):
        return round(self.native.ActualOffset.Y)

    @property
    def width(self):
        if hasattr(self.native, "Width") and isfinite(self.native.Width):
            return round(self.native.Width)
        if self.native.ActualSize.X:
            return round(self.native.ActualSize.X)
        return 0

    @property
    def height(self):
        if hasattr(self.native, "Height") and isfinite(self.native.Height):
            return round(self.native.Height)
        if self.native.ActualSize.Y:
            return round(self.native.ActualSize.Y)
        return 0

    def assert_width(self, min_width, max_width):
        assert min_width <= self.width <= max_width

    def assert_height(self, min_height, max_height):
        if self.fixed_height is not None:
            assert self.height == approx(self.fixed_height, rel=0.1)
        else:
            assert min_height <= self.height <= max_height

    def assert_image_size(self, image_size, size, screen, window=None):
        scale_factor = (
            window._impl.get_current_screen().dpi_scale
            if window is not None
            else screen._impl.dpi_scale
        )
        assert image_size == approx(
            (round(size[0] * scale_factor), round(size[1] * scale_factor)),
            abs=1,
        )
