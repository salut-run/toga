from win32more import String
from win32more.Microsoft.UI.Windowing import DisplayArea
from win32more.Microsoft.UI.Xaml import ApplicationTheme
from win32more.Microsoft.UI.Xaml.Controls import ContentDialog, TextBlock
from win32more.Windows.Win32.Media.Audio import SND_ALIAS, SND_ASYNC, PlaySound
from win32more.Windows.Win32.UI.WindowsAndMessaging import ShowCursor

from .libs.nativeapp import NativeApp
from .libs.proactor import WinUI3ProactorEventLoop
from .screens import Screen as ScreenImpl


class App:
    # Windows applications exit when the last window is closed.
    CLOSE_ON_LAST_WINDOW = True
    # Windows applications use default command line handling.
    HANDLES_COMMAND_LINE = False

    def __init__(self, interface):
        self.interface = interface
        self.interface._impl = self

        # Track whether the app is exiting.
        self._is_exiting = False
        self._exiting_presentation = False
        self._current_window = None

        # The Win32 function ShowCursor is used to show and hide the cursor. Here cursor
        # visibility is represented by a display count. For example, if hide is called N
        # times then to make the cursor re-appear, show must be called N times as well.
        # Hence, a local boolean is stored to avoid a deep stack.
        self._cursor_visible = True

        self.loop = WinUI3ProactorEventLoop()
        self.native_instance: NativeApp | None = None
        self._about_dialog = None

    def create(self):
        self.native = NativeApp

        # Populate the main window as soon as the event loop is running.
        self.loop.call_soon_threadsafe(self.interface._startup)

    ####################################################################################
    # Commands and menus
    ####################################################################################

    def create_standard_commands(self):
        # The standard commands for WinUI 3 are already created by the Toga core
        # interface by calling _create_standard_commands() during _startup().
        pass

    def create_menus(self):
        """Creates menu bars for the windows with the 'create_menus' attribute."""
        for window in self.interface.windows:
            # From toga_winforms:
            # It's difficult to trigger this on a simple window, because we can't easily
            # modify the set of app-level commands that are registered, and a simple
            # window doesn't exist when the app starts up. Therefore, no-branch the else
            # case.
            if hasattr(window._impl, "create_menus"):  # pragma: no branch
                window._impl.create_menus()

    ####################################################################################
    # App lifecycle
    ####################################################################################

    def exit(self):  # pragma: no cover
        self._is_exiting = True
        if self.native_instance is not None:
            self.native_instance.Exit()

    def main_loop(self):
        self.create()
        self.loop.run_forever(self)

    def set_icon(self, icon):
        for window in self.interface.windows:
            window._impl.set_icon(icon)

    def set_main_window(self, window):
        pass

    ####################################################################################
    # App resources
    ####################################################################################

    def get_primary_screen(self):
        """Returns the WinUI 3 Screen object for the primary screen."""
        return ScreenImpl(DisplayArea.Primary)

    def get_screens(self):
        """Gets a list of WinUI 3 Screen objects corresponding to the system's screens.

        The primary screen has index 0 within the returned list.
        """
        primary_screen = self.get_primary_screen()
        screen_list = [primary_screen] + [
            ScreenImpl(native=screen)
            for screen in DisplayArea.FindAll()
            if ScreenImpl(native=screen) != primary_screen
        ]
        return screen_list

    ####################################################################################
    # App state
    ####################################################################################

    def get_dark_mode_state(self) -> bool:
        """Returns True if the NativeApp instance is in dark mode."""
        return self.native_instance.RequestedTheme == ApplicationTheme.Dark

    ####################################################################################
    # App capabilities
    ####################################################################################

    def beep(self):
        """Plays the 'SystemAsterisk' sound."""
        # learn.microsoft.com/windows/win32/multimedia/the-playsound-function
        PlaySound(String("SystemAsterisk"), None, SND_ALIAS | SND_ASYNC)

    def show_about_dialog(self):
        message_parts = []
        if self.interface.version is not None:
            message_parts.append(
                f"{self.interface.formal_name} v{self.interface.version}"
            )
        else:
            message_parts.append(self.interface.formal_name)

        if self.interface.author is not None:
            message_parts.append(f"Author: {self.interface.author}")
        if self.interface.description is not None:
            message_parts.append(f"\n{self.interface.description}")
        if self.interface.home_page is not None:
            message_parts.append(f"\n{self.interface.home_page}")

        content = TextBlock()
        content.Text = "\n".join(message_parts)

        self._about_dialog = ContentDialog()
        self._about_dialog.Title = f"About {self.interface.formal_name}"
        self._about_dialog.Content = content
        self._about_dialog.CloseButtonText = "OK"
        self._about_dialog.XamlRoot = (
            self.interface.main_window._impl.content_native.XamlRoot
        )
        self._about_dialog.Closed += self.native_event_about_dialog_closed
        self._about_dialog.ShowAsync()

    def native_event_about_dialog_closed(self, sender, args):
        self._about_dialog = None

    ####################################################################################
    # Cursor control
    ####################################################################################

    def hide_cursor(self):
        # learn.microsoft.com/windows/win32/api/winuser/nf-winuser-showcursor
        if self._cursor_visible:
            ShowCursor(False)
        self._cursor_visible = False

    def show_cursor(self):
        # learn.microsoft.com/windows/win32/api/winuser/nf-winuser-showcursor
        if not self._cursor_visible:
            ShowCursor(True)
        self._cursor_visible = True

    ####################################################################################
    # Window control
    ####################################################################################

    def get_current_window(self):
        """Returns the currently activated window if one exists, otherwise None."""
        visible_windows = [
            window._impl
            for window in self.interface.windows
            if window._impl.get_visible()
        ]
        document_windows = [
            window._impl
            for window in self.interface.windows
            if hasattr(window, "doc") and window._impl.get_visible()
        ]
        if len(document_windows) == 1:
            return document_windows[0]

        if self._current_window in visible_windows:
            return self._current_window

        for window in visible_windows:
            if window.is_activated:
                return window
        return None

    def set_current_window(self, window):
        """Brings a given window to the foreground and gives it input focus."""
        self._current_window = window._impl
        window._impl.native.Activate()
