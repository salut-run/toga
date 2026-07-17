import asyncio
import html
import json

from travertino.size import at_least

import toga
from toga.handlers import WeakrefCallable

from ._webview import WebView2Widget

LEAFLET_VERSION = "1.9.4"
LEAFLET_BASE_URL = f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist"
LEAFLET_SCRIPT_URL = f"{LEAFLET_BASE_URL}/leaflet.js"
LEAFLET_STYLESHEET_URL = f"{LEAFLET_BASE_URL}/leaflet.css"
MAP_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
MAP_ATTRIBUTION = "&copy; OpenStreetMap contributors"
MAP_PROVIDER_LOAD_TIMEOUT_MS = 15000


MAP_PROVIDER = {
    "leafletVersion": LEAFLET_VERSION,
    "leafletScript": LEAFLET_SCRIPT_URL,
    "leafletStylesheet": LEAFLET_STYLESHEET_URL,
    "tileUrl": MAP_TILE_URL,
    "attribution": MAP_ATTRIBUTION,
    "providerLoadTimeout": MAP_PROVIDER_LOAD_TIMEOUT_MS,
}


def mapview_html_content():
    stylesheet_url = html.escape(LEAFLET_STYLESHEET_URL, quote=True)
    script_url = html.escape(LEAFLET_SCRIPT_URL, quote=True)
    provider_payload = json.dumps(MAP_PROVIDER)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="{stylesheet_url}">
    <style>
        html, body, #map {{
            width: 100%;
            height: 100%;
            margin: 0;
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        const togaMapProvider = {provider_payload};
        const mapElement = document.getElementById("map");
        const pins = {{}};
        const pendingActions = [];
        let map = null;
        let tileLayer = null;
        let providerUnavailable = false;
        let providerLoadTimer = null;
        let currentLocation = [-31.9559, 115.8606];
        let currentZoom = 11;

        window.togaMapProvider = togaMapProvider;
        mapElement.dataset.mapStatus = "loading";

        if (togaMapProvider.providerLoadTimeout > 0) {{
            providerLoadTimer = window.setTimeout(
                markProviderUnavailable,
                togaMapProvider.providerLoadTimeout
            );
        }}

        function markProviderUnavailable() {{
            if (providerLoadTimer) {{
                window.clearTimeout(providerLoadTimer);
                providerLoadTimer = null;
            }}
            if (!map) {{
                providerUnavailable = true;
                pendingActions.length = 0;
                mapElement.dataset.mapStatus = "provider-unavailable";
            }}
        }}

        function withMap(action) {{
            if (map) {{
                action();
            }} else if (!providerUnavailable) {{
                pendingActions.push(action);
            }}
        }}

        function initializeMap() {{
            if (providerUnavailable) {{
                return;
            }}
            if (providerLoadTimer) {{
                window.clearTimeout(providerLoadTimer);
                providerLoadTimer = null;
            }}
            if (typeof L === "undefined") {{
                markProviderUnavailable();
                return;
            }}

            map = L.map("map").setView(currentLocation, currentZoom);
            tileLayer = L.tileLayer(togaMapProvider.tileUrl, {{
                maxZoom: 20,
                attribution: togaMapProvider.attribution
            }}).addTo(map);
            mapElement.dataset.mapStatus = "ready";

            while (pendingActions.length) {{
                pendingActions.shift()();
            }}
        }}

        function setLocation(latitude, longitude) {{
            currentLocation = [latitude, longitude];
            withMap(() => map.panTo(currentLocation));
        }}

        function setZoom(zoom) {{
            currentZoom = zoom;
            withMap(() => map.setZoom(zoom));
        }}

        function addPin(id, latitude, longitude, popup) {{
            withMap(() => {{
                removePin(id);
                const marker = L.marker([latitude, longitude]).addTo(map);
                marker.bindPopup(popup);
                marker.on("click", () => chrome.webview.postMessage(id));
                pins[id] = marker;
            }});
        }}

        function updatePin(id, latitude, longitude, popup) {{
            withMap(() => {{
                if (pins[id]) {{
                    pins[id].setLatLng([latitude, longitude]).setPopupContent(popup);
                }}
            }});
        }}

        function removePin(id) {{
            withMap(() => {{
                if (pins[id]) {{
                    map.removeLayer(pins[id]);
                    delete pins[id];
                }}
            }});
        }}
    </script>
    <script
        src="{script_url}"
        onload="initializeMap()"
        onerror="markProviderUnavailable()"
    ></script>
</body>
</html>
"""


def pin_id(pin):
    return hex(id(pin))


def popup(pin):
    title = html.escape(str(pin.title))
    if pin.subtitle:
        return f"<b>{title}</b><br>{html.escape(str(pin.subtitle))}"
    return f"<b>{title}</b>"


class MapView(WebView2Widget):
    SUPPORTS_ON_SELECT = True

    def create(self):
        self._create_webview2()
        self.native.IsTabStop = True
        self.native.NavigationCompleted += WeakrefCallable(
            self.native_event_navigation_completed
        )

        self.backlog = []
        self._map_navigation_pending = False
        self._location = toga.LatLng(-31.9559, 115.8606)
        self._zoom = 11
        self._pins = set()
        self._pin_lookup = {}
        self._start_webview2()

    def _webview2_ready(self):
        self.native.CoreWebView2.Settings.IsWebMessageEnabled = True
        self.native.CoreWebView2.WebMessageReceived += WeakrefCallable(
            self.native_event_web_message_received
        )
        self._map_navigation_pending = True
        self.native.NavigateToString(mapview_html_content())

    def _webview2_failed(self):
        self.backlog = None

    def native_event_navigation_completed(self, sender, args):
        if self._map_navigation_pending and self.backlog is not None:
            self._map_navigation_pending = False
            backlog = self.backlog
            self.backlog = None
            for javascript in backlog:
                self._execute(javascript)

    def native_event_web_message_received(self, sender, args):
        try:
            pin = self._pin_lookup[args.TryGetWebMessageAsString()]
        except KeyError:
            pass
        else:
            self.interface.on_select(pin=pin)

    def _execute(self, javascript):
        async def execute():
            try:
                await self.native.ExecuteScriptAsync(javascript)
            except Exception:  # pragma: nocover
                pass

        asyncio.create_task(execute())

    def _invoke(self, javascript):
        if self.corewebview2_available is False:
            return
        elif self.backlog is None:
            self._execute(javascript)
        else:
            self.backlog.append(javascript)

    def get_location(self):
        return self._location

    def set_location(self, position):
        self._location = toga.LatLng(*position)
        self._invoke(f"setLocation({self._location.lat}, {self._location.lng});")

    def get_zoom(self):
        return self._zoom

    def set_zoom(self, zoom):
        self._zoom = zoom
        self._invoke(f"setZoom({zoom});")

    def tile_longitude_span(self):
        return 360 / (2**self._zoom)

    def add_pin(self, pin):
        pin._native = pin_id(pin)
        self._pins.add(pin)
        self._pin_lookup[pin._native] = pin
        self._invoke(
            f"addPin({json.dumps(pin._native)}, "
            f"{pin.location.lat}, {pin.location.lng}, {json.dumps(popup(pin))});"
        )

    def update_pin(self, pin):
        self._invoke(
            f"updatePin({json.dumps(pin._native)}, "
            f"{pin.location.lat}, {pin.location.lng}, {json.dumps(popup(pin))});"
        )

    def remove_pin(self, pin):
        self._pins.remove(pin)
        self._pin_lookup.pop(pin._native, None)
        self._invoke(f"removePin({json.dumps(pin._native)});")
        pin._native = None

    @property
    def pin_count(self):
        return len(self._pins)

    def select_pin(self, pin):
        self.interface.on_select(pin=pin)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
