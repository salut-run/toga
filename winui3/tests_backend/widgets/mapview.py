import asyncio

from win32more.Microsoft.UI.Xaml.Controls import WebView2

from .base import SimpleProbe


class MapViewProbe(SimpleProbe):
    native_class = WebView2

    async def tile_longitude_span(self):
        return self.impl.tile_longitude_span()

    @property
    def pin_count(self):
        return self.impl.pin_count

    async def select_pin(self, pin):
        self.impl.select_pin(pin)
        await self.redraw(f"{pin.title} pin has been selected")

    async def wait_for_map(self, message, max_delay=0.5):
        await asyncio.sleep(0)
        await self.redraw(
            message,
            delay=max_delay,
            wait_for=lambda: self.impl.backlog is None,
        )
