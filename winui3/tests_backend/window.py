from win32more import unbox_value
from win32more.Microsoft.UI.Interop import GetWindowFromWindowId
from win32more.Microsoft.UI.Windowing import OverlappedPresenterState
from win32more.Microsoft.UI.Xaml import Window as NativeWindow
from win32more.Microsoft.UI.Xaml.Controls import (
    AppBarButton,
    AppBarSeparator,
    ICommandBarElement,
    ToolTipService,
)
from win32more.Windows.Foundation.Collections import IVector
from win32more.Windows.Win32.Foundation import LPARAM, WPARAM
from win32more.Windows.Win32.UI.WindowsAndMessaging import (
    SC_MINIMIZE,
    SC_RESTORE,
    WM_CLOSE,
    WM_SYSCOMMAND,
    PostMessage,
)

from toga import Size
from toga.constants import WindowState

from .dialogs import DialogsMixin
from .probe import BaseProbe


class WindowProbe(BaseProbe, DialogsMixin):
    supports_closable = False
    supports_minimizable = True
    supports_move_while_hidden = True
    supports_unminimize = True
    supports_minimize = True
    supports_placement = True
    supports_as_image = False
    supports_focus = True
    fullscreen_presentation_equal_size = True
    maximize_fullscreen_presentation_equal_size = False

    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.impl = window._impl
        super().__init__(window._impl.native)
        assert isinstance(self.native, NativeWindow)

    async def wait_for_window(self, message, state=None):
        await self.redraw(message, delay=0.1)

    async def cleanup(self):
        self.window.close()
        await self.redraw("Closing window")

    def close(self):
        PostMessage(
            GetWindowFromWindowId(self.native.AppWindow.Id),
            WM_CLOSE,
            WPARAM(0),
            LPARAM(0),
        )

    @property
    def content_size(self):
        return self.client_size

    @property
    def client_size(self):
        return Size(
            round(self.native.Bounds.Width),
            round(self.native.Bounds.Height),
        )

    @property
    def is_resizable(self):
        return self.window.resizable

    @property
    def is_minimizable(self):
        return self.window.minimizable

    @property
    def is_minimized(self):
        return self.instantaneous_state == WindowState.MINIMIZED

    def minimize(self):
        if not self.window.minimizable:
            return

        PostMessage(
            GetWindowFromWindowId(self.native.AppWindow.Id),
            WM_SYSCOMMAND,
            WPARAM(SC_MINIMIZE),
            LPARAM(0),
        )

    def unminimize(self):
        PostMessage(
            GetWindowFromWindowId(self.native.AppWindow.Id),
            WM_SYSCOMMAND,
            WPARAM(SC_RESTORE),
            LPARAM(0),
        )

    @property
    def container_probe(self):
        return BaseProbe(self.impl.container_native)

    @property
    def instantaneous_state(self):
        presenter = self.native.AppWindow.Presenter
        if getattr(presenter, "State", None) == OverlappedPresenterState.Minimized:
            return WindowState.MINIMIZED
        return self.impl.get_window_state(in_progress_state=False)

    @property
    def menubar_probe(self):
        if hasattr(self.impl, "menu_native"):
            return BaseProbe(self.impl.menu_native)
        return None

    @property
    def toolbar_probe(self):
        if self.impl.toolbar_native is None:
            return None
        return BaseProbe(self.impl.toolbar_native)

    def has_toolbar(self):
        return self.impl.toolbar_native is not None

    def _native_toolbar_item(self, index):
        return self.impl.toolbar_native.PrimaryCommands.as_(
            IVector[ICommandBarElement]
        ).GetAt(index)

    def assert_is_toolbar_separator(self, index, section=False):
        assert isinstance(
            self._native_toolbar_item(index).as_(AppBarSeparator),
            AppBarSeparator,
        )

    def assert_toolbar_item(self, index, label, tooltip, has_icon, enabled):
        item = self._native_toolbar_item(index).as_(AppBarButton)
        assert isinstance(item, AppBarButton)
        assert item.Label == label
        native_tooltip = ToolTipService.GetToolTip(item)
        tooltip_text = None if native_tooltip is None else unbox_value(native_tooltip)
        assert tooltip_text == tooltip
        assert (item.Icon is not None) == has_icon
        assert item.IsEnabled == enabled

    def press_toolbar_button(self, index):
        self.impl.toolbar_commands[index].action()
