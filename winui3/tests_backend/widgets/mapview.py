import asyncio
import json
from time import time

from win32more.Microsoft.UI.Xaml.Controls import WebView2

from toga_winui3.widgets.mapview import LEAFLET_BASE_URL, LEAFLET_VERSION, MAP_TILE_URL

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

    async def map_surface_state(self):
        return json.loads(
            await self.impl.native.ExecuteScriptAsync(
                """
                (() => {
                    const mapElement = document.getElementById("map");
                    return {
                        hasMapElement: !!mapElement,
                        status: mapElement ? mapElement.dataset.mapStatus : null,
                        provider: window.togaMapProvider || null,
                        leafletStylesheets: Array.from(
                            document.querySelectorAll('link[rel="stylesheet"]')
                        ).map((link) => link.href),
                        leafletScripts: Array.from(document.scripts)
                            .map((script) => script.src)
                            .filter((src) => src),
                        hasLeaflet: typeof L !== "undefined",
                        hasMap: typeof map !== "undefined" && map !== null,
                        hasTileLayer: (
                            typeof tileLayer !== "undefined" && tileLayer !== null
                        ),
                        pinCount: (
                            typeof pins !== "undefined"
                                ? Object.keys(pins).length
                                : null
                        ),
                        pendingActionCount: (
                            typeof pendingActions !== "undefined"
                                ? pendingActions.length
                                : null
                        ),
                    };
                })();
                """
            )
        )

    async def assert_map_surface(self, message, expected_pin_count=0, max_delay=2):
        deadline = time() + max_delay
        while True:
            await self.redraw(message)
            state = await self.map_surface_state()
            if state["status"] != "loading" or time() >= deadline:
                break
            await asyncio.sleep(0.05)

        assert state["hasMapElement"]
        assert state["status"] in {"loading", "ready", "provider-unavailable"}
        assert state["provider"] == {
            "leafletVersion": LEAFLET_VERSION,
            "leafletScript": f"{LEAFLET_BASE_URL}/leaflet.js",
            "leafletStylesheet": f"{LEAFLET_BASE_URL}/leaflet.css",
            "tileUrl": MAP_TILE_URL,
            "attribution": "&copy; OpenStreetMap contributors",
        }
        assert f"{LEAFLET_BASE_URL}/leaflet.css" in state["leafletStylesheets"]
        assert f"{LEAFLET_BASE_URL}/leaflet.js" in state["leafletScripts"]

        if state["status"] == "ready":
            assert state["hasLeaflet"]
            assert state["hasMap"]
            assert state["hasTileLayer"]
            assert state["pinCount"] == expected_pin_count
            assert state["pendingActionCount"] == 0
        elif state["status"] == "provider-unavailable":
            assert not state["hasMap"]

        return state
