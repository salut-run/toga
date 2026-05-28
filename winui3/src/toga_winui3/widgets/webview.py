import asyncio
import hashlib
import json
import shutil
from http.cookiejar import Cookie, CookieJar

from win32more.Windows.Foundation import Uri

import toga
from toga.handlers import WeakrefCallable
from toga.widgets.webview import CookiesResult, JavaScriptResult

from ._webview import WebView2Widget


def requires_initialization(method):
    def wrapper(self, *args, **kwargs):
        def task():
            method(self, *args, **kwargs)

        self.run_after_initialization(task)

    return wrapper


class WebView(WebView2Widget):
    def create(self):
        self._create_webview2()
        self.native.NavigationCompleted += WeakrefCallable(
            self.native_event_navigation_completed
        )
        self.native.NavigationStarting += WeakrefCallable(
            self.native_event_navigation_starting
        )

        self.pending_tasks = []
        self.loaded_future = None
        self.default_user_agent = ""
        self.cookie_manager = None
        self._allowed_url = None
        self._url = None
        self._large_content_dir = (
            toga.App.app.paths.cache / f"toga/webview-{self.interface.id}"
        )

        self._start_webview2()

    def __del__(self):  # pragma: nocover
        shutil.rmtree(self._large_content_dir, ignore_errors=True)

    def _webview2_ready(self):
        settings = self.native.CoreWebView2.Settings
        self.default_user_agent = settings.UserAgent
        settings.AreBrowserAcceleratorKeysEnabled = True
        settings.AreDefaultContextMenusEnabled = True
        settings.AreDefaultScriptDialogsEnabled = True
        settings.AreDevToolsEnabled = True
        settings.IsBuiltInErrorPageEnabled = True
        settings.IsScriptEnabled = True
        settings.IsStatusBarEnabled = True
        settings.IsWebMessageEnabled = True
        settings.IsSwipeNavigationEnabled = False
        settings.IsZoomControlEnabled = True

        self.cookie_manager = self.native.CoreWebView2.CookieManager

        for task in self.pending_tasks:
            task()
        self.pending_tasks = None

    def _webview2_failed(self):
        self.pending_tasks = None

    def run_after_initialization(self, task):
        if self.corewebview2_available:
            task()
        elif self.pending_tasks is not None:
            self.pending_tasks.append(task)

    def native_event_navigation_completed(self, sender, args):
        self.interface.on_webview_load()

        if self.loaded_future:
            self.loaded_future.set_result(None)
            self.loaded_future = None

    def native_event_navigation_starting(self, sender, event):
        if self.interface.on_navigation_starting._raw:
            if self._allowed_url == "about:blank" or self._allowed_url == event.Uri:
                allow = True
            else:
                self._allowed_url = None
                result = self.interface.on_navigation_starting(url=event.Uri)
                allow = result if isinstance(result, bool) else False

            if not allow:
                event.Cancel = True
            else:
                self._url = self._normalize_url(event.Uri)
        else:
            self._url = self._normalize_url(event.Uri)

    def _normalize_url(self, url):
        return None if url in {None, "", "about:blank"} else str(url)

    def get_url(self):
        return self._url

    @requires_initialization
    def set_url(self, value, future=None):
        if self.interface.on_navigation_starting._raw:
            self._allowed_url = "about:blank" if value is None else value

        self.loaded_future = future
        self._url = value

        if value is None:
            self.native.NavigateToString("")
        else:
            self.native.Source = Uri(value)

    @requires_initialization
    def set_content(self, root_url, content):
        if self.interface.on_navigation_starting._raw:
            self._allowed_url = "about:blank"

        if len(content) > 1572834:
            self._large_content_dir.mkdir(parents=True, exist_ok=True)
            h = hashlib.new("sha1")
            h.update(bytes(self.interface.id, "utf-8"))
            h.update(bytes("" if root_url is None else root_url, "utf-8"))
            file_path = self._large_content_dir / f"{h.hexdigest()}.html"
            file_path.write_text(content, encoding="utf-8")

            self._url = file_path.as_uri()
            self.native.Source = Uri(self._url)
        else:
            self._url = None
            self.native.NavigateToString(content)

    def get_user_agent(self):
        if self.corewebview2_available:
            return self.native.CoreWebView2.Settings.UserAgent
        return ""

    @requires_initialization
    def set_user_agent(self, value):
        self.native.CoreWebView2.Settings.UserAgent = (
            self.default_user_agent if value is None else value
        )

    def get_cookies(self):
        result = CookiesResult()

        async def get_cookies():
            try:
                cookies = await self.cookie_manager.GetCookiesAsync(None)
            except Exception as exc:  # pragma: nocover
                result.set_exception(exc)
                return

            cookie_jar = CookieJar()
            for cookie in cookies:
                cookie_jar.set_cookie(
                    Cookie(
                        version=0,
                        name=cookie.Name,
                        value=cookie.Value,
                        port=None,
                        port_specified=False,
                        domain=cookie.Domain,
                        domain_specified=True,
                        domain_initial_dot=False,
                        path=cookie.Path,
                        path_specified=True,
                        secure=cookie.IsSecure,
                        expires=None,
                        discard=cookie.IsSession,
                        comment=None,
                        comment_url=None,
                        rest={},
                        rfc2109=False,
                    )
                )

            result.set_result(cookie_jar)

        self.run_after_initialization(lambda: asyncio.create_task(get_cookies()))
        return result

    def evaluate_javascript(self, javascript, on_result=None):
        result = JavaScriptResult(on_result)

        async def evaluate():
            try:
                value = json.loads(await self.native.ExecuteScriptAsync(javascript))
            except Exception:
                value = None

            result.set_result(value)

        self.run_after_initialization(lambda: asyncio.create_task(evaluate()))
        return result
