import asyncio

from pytest import approx


class BaseProbe:
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
        return round(self.native.ActualSize.X)

    @property
    def height(self):
        return round(self.native.ActualSize.Y)

    def assert_width(self, min_width, max_width):
        assert min_width <= self.width <= max_width

    def assert_height(self, min_height, max_height):
        if self.fixed_height is not None:
            assert self.height == approx(self.fixed_height, rel=0.1)
        else:
            assert min_height <= self.height <= max_height

    def assert_image_size(self, image_size, size, screen, window=None):
        assert image_size == size
