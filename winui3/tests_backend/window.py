from win32more.Microsoft.UI.Windowing import OverlappedPresenterState
from win32more.Microsoft.UI.Xaml import Window as NativeWindow

from toga import Size
from toga.constants import WindowState

from .probe import BaseProbe


class WindowProbe(BaseProbe):
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
        self.native.Close()

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
        self.native.AppWindow.Presenter.Minimize()

    def unminimize(self):
        self.native.AppWindow.Presenter.Restore()

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
        return None

    def has_toolbar(self):
        return False

    def assert_is_toolbar_separator(self, index, section=False):
        raise AssertionError("WinUI 3 toolbar probing is not implemented yet.")

    def assert_toolbar_item(self, index, label, tooltip, has_icon, enabled):
        raise AssertionError("WinUI 3 toolbar probing is not implemented yet.")

    def press_toolbar_button(self, index):
        raise AssertionError("WinUI 3 toolbar probing is not implemented yet.")
