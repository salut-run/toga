import asyncio
import html
import json
from weakref import ref

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import WebView2
from win32more.Windows.Foundation import AsyncStatus
from win32more.Windows.UI import Color

import toga
from toga.handlers import WeakrefCallable

from .base import Widget

LEAFLET_VERSION = "1.9.4"
LEAFLET_BASE_URL = f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist"
MAP_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

MAPVIEW_HTML_CONTENT = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="{LEAFLET_BASE_URL}/leaflet.css">
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
        const togaMapProvider = {{
            leafletVersion: {json.dumps(LEAFLET_VERSION)},
            leafletScript: {json.dumps(f"{LEAFLET_BASE_URL}/leaflet.js")},
            leafletStylesheet: {json.dumps(f"{LEAFLET_BASE_URL}/leaflet.css")},
            tileUrl: {json.dumps(MAP_TILE_URL)},
            attribution: "&copy; OpenStreetMap contributors",
        }};
        const mapElement = document.getElementById("map");
        const pins = {{}};
        const pendingActions = [];
        let map = null;
        let tileLayer = null;
        let currentLocation = [-31.9559, 115.8606];
        let currentZoom = 11;

        window.togaMapProvider = togaMapProvider;
        mapElement.dataset.mapStatus = "loading";

        function markProviderUnavailable() {{
            if (!map) {{
                mapElement.dataset.mapStatus = "provider-unavailable";
            }}
        }}

        function withMap(action) {{
            if (map) {{
                action();
            }} else {{
                pendingActions.push(action);
            }}
        }}

        function initializeMap() {{
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
        src="{LEAFLET_BASE_URL}/leaflet.js"
        onload="initializeMap()"
        onerror="markProviderUnavailable()"
    ></script>
</body>
</html>
"""


def pin_id(pin):
    return hex(id(pin))


def latlng(location):
    return f"[{location.lat}, {location.lng}]"


def popup(pin):
    title = html.escape(str(pin.title))
    if pin.subtitle:
        return f"<b>{title}</b><br>{html.escape(str(pin.subtitle))}"
    return f"<b>{title}</b>"


class MapView(Widget):
    SUPPORTS_ON_SELECT = True

    def create(self):
        self.native = WebView2()
        self.native.DefaultBackgroundColor = Color(A=0, R=0, G=0, B=0)
        self.native.IsTabStop = True
        self.native.NavigationCompleted += WeakrefCallable(
            self.native_event_navigation_completed
        )

        self.backlog = []
        self._initialization_action = None
        self.corewebview2_available = None
        self._location = toga.LatLng(-31.9559, 115.8606)
        self._zoom = 11
        self._pins = set()
        self._pin_lookup = {}

        self_ref = ref(self)

        def initialization_completed(async_info, async_status):
            if impl := self_ref():
                impl._initialization_action = None
                impl._initialize_core_webview2(async_info, async_status)

        self._initialization_action = self.native.EnsureCoreWebView2Async()
        self._initialization_action.Completed = initialization_completed

    def _initialize_core_webview2(self, async_info, async_status):
        if async_status != AsyncStatus.Completed:  # pragma: nocover
            self.corewebview2_available = False
            self.backlog = None
            print(f"MapView WebView2 initialization failed: {async_status}")
            return

        try:
            async_info.GetResults()
        except Exception as exc:  # pragma: nocover
            self.corewebview2_available = False
            self.backlog = None
            print(f"MapView WebView2 initialization failed: {exc}")
            return

        self.corewebview2_available = True
        self.native.CoreWebView2.Settings.IsWebMessageEnabled = True
        self.native.CoreWebView2.WebMessageReceived += WeakrefCallable(
            self.native_event_web_message_received
        )
        self.native.NavigateToString(MAPVIEW_HTML_CONTENT)

    def native_event_navigation_completed(self, sender, args):
        if self.backlog is not None:
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
            except Exception as exc:  # pragma: nocover
                print(f"MapView JavaScript failed: {exc}")

        asyncio.create_task(execute())

    def _invoke(self, javascript):
        if self.backlog is None:
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
