from weakref import ref

from win32more.Microsoft.UI.Xaml.Controls import WebView2
from win32more.Windows.Foundation import AsyncStatus
from win32more.Windows.UI import Color

from .base import Widget


class WebView2Widget(Widget):
    """Shared WebView2 activation and failure handling."""

    def _create_webview2(self):
        self.native = WebView2()
        self.native.DefaultBackgroundColor = Color(A=0, R=0, G=0, B=0)
        self.corewebview2_available = None
        self._initialization_action = None
        self._webview2_initialization_error = None

    def _start_webview2(self):
        self_ref = ref(self)

        def initialization_completed(async_info, async_status):
            if impl := self_ref():
                impl._initialization_action = None
                impl._initialize_core_webview2(async_info, async_status)

        self._initialization_action = self.native.EnsureCoreWebView2Async()
        self._initialization_action.Completed = initialization_completed

    def _initialize_core_webview2(self, async_info, async_status):
        if async_status != AsyncStatus.Completed:  # pragma: nocover
            self._handle_webview2_initialization_failure(async_status)
            return

        try:
            async_info.GetResults()
        except Exception as exc:  # pragma: nocover
            self._handle_webview2_initialization_failure(exc)
            return

        self.corewebview2_available = True
        self._webview2_initialization_error = None
        self._webview2_ready()

    def _handle_webview2_initialization_failure(self, error):
        self.corewebview2_available = False
        self._webview2_initialization_error = str(error)
        self._webview2_failed()

    def _webview2_ready(self):
        raise NotImplementedError

    def _webview2_failed(self):
        pass
