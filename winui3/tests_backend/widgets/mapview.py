import asyncio
import json
from time import time

from win32more.Microsoft.UI.Xaml.Controls import WebView2

import toga
from toga_winui3.widgets.mapview import (
    LEAFLET_SCRIPT_URL,
    LEAFLET_STYLESHEET_URL,
    MAP_PROVIDER,
    mapview_html_content,
)

from .base import SimpleProbe

UNAVAILABLE_SCRIPT_URL = "https://example.invalid/toga-winui3-leaflet.js"
UNAVAILABLE_STYLESHEET_URL = "https://example.invalid/toga-winui3-leaflet.css"
UNAVAILABLE_MAP_PROVIDER = {
    **MAP_PROVIDER,
    "leafletScript": UNAVAILABLE_SCRIPT_URL,
    "leafletStylesheet": UNAVAILABLE_STYLESHEET_URL,
    "providerLoadTimeout": 1,
}


def unavailable_mapview_html():
    content = mapview_html_content().replace(
        json.dumps(MAP_PROVIDER),
        json.dumps(UNAVAILABLE_MAP_PROVIDER),
    )
    return content.replace(LEAFLET_SCRIPT_URL, UNAVAILABLE_SCRIPT_URL).replace(
        LEAFLET_STYLESHEET_URL,
        UNAVAILABLE_STYLESHEET_URL,
    )


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
        assert self.impl.corewebview2_available is True, (
            self.impl._webview2_initialization_error
        )
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
                        providerUnavailable: (
                            typeof providerUnavailable !== "undefined"
                                ? providerUnavailable
                                : null
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
        assert state["provider"] == MAP_PROVIDER
        assert LEAFLET_STYLESHEET_URL in state["leafletStylesheets"]
        assert LEAFLET_SCRIPT_URL in state["leafletScripts"]

        if state["status"] == "ready":
            assert not state["providerUnavailable"]
            assert state["hasLeaflet"]
            assert state["hasMap"]
            assert state["hasTileLayer"]
            assert state["pinCount"] == expected_pin_count
            assert state["pendingActionCount"] == 0
        elif state["status"] == "provider-unavailable":
            assert state["providerUnavailable"]
            assert not state["hasMap"]
            assert state["pendingActionCount"] == 0

        return state

    async def assert_provider_unavailable_surface(self):
        assert self.impl.corewebview2_available is True, (
            self.impl._webview2_initialization_error
        )
        self.impl.native.NavigateToString(unavailable_mapview_html())

        deadline = time() + 2
        while True:
            await self.redraw("Map provider unavailable state simulated")
            state = await self.map_surface_state()
            if state.get("status") == "provider-unavailable" or time() >= deadline:
                break
            await asyncio.sleep(0.05)

        assert state["hasMapElement"]
        assert state["status"] == "provider-unavailable"
        assert state["provider"] == UNAVAILABLE_MAP_PROVIDER
        assert state["providerUnavailable"]
        assert not state["hasMap"]
        assert state["pinCount"] == 0
        assert state["pendingActionCount"] == 0

        self.widget.location = (-33.955, 115.075)
        self.widget.zoom = 12
        self.widget.pins.add(toga.MapPin((-31.9602, 115.8325), title="Kings Park"))
        await self.redraw("Map provider unavailable drops queued actions")
        state = await self.map_surface_state()

        assert state["status"] == "provider-unavailable"
        assert state["providerUnavailable"]
        assert state["pinCount"] == 0
        assert state["pendingActionCount"] == 0

    async def assert_webview2_initialization_failure(self):
        executed_javascript = []
        original_execute = self.impl._execute

        try:
            self.impl._execute = executed_javascript.append
            self.impl._handle_webview2_initialization_failure("probe failure")

            assert self.impl.corewebview2_available is False
            assert self.impl.backlog is None
            assert self.impl._webview2_initialization_error == "probe failure"

            self.widget.location = (-33.955, 115.075)
            self.widget.zoom = 12
            self.widget.pins.add(toga.MapPin((-31.9602, 115.8325), title="Kings Park"))
            await self.redraw("MapView WebView2 initialization failure simulated")

            assert self.widget.location.lat == -33.955
            assert self.widget.location.lng == 115.075
            assert self.widget.zoom == 12
            assert self.impl.pin_count == 1
            assert executed_javascript == []
        finally:
            self.impl._execute = original_execute
