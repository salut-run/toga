from __future__ import annotations

from ctypes import byref
from pathlib import Path
from typing import TYPE_CHECKING

from win32more import UInt32
from win32more.Microsoft.UI.Interop import GetWindowFromWindowId
from win32more.Microsoft.UI.Windowing import (
    AppWindowPresenterKind,
    DisplayArea,
    DisplayAreaFallback,
    OverlappedPresenter,
    OverlappedPresenterState,
    TitleBarTheme,
)
from win32more.Microsoft.UI.Xaml import (
    HorizontalAlignment,
    VerticalAlignment,
    Visibility,
    WindowActivationState,
)
from win32more.Microsoft.UI.Xaml.Controls import (
    AppBarButton,
    AppBarSeparator,
    Canvas,
    CommandBar,
    CommandBarDefaultLabelPosition,
    Grid,
    ICommandBarElement,
    ImageIcon,
    MenuBar,
    MenuBarItem,
    MenuFlyoutItem,
    MenuFlyoutSeparator,
    MenuFlyoutSubItem,
    ToolTipService,
)
from win32more.Microsoft.UI.Xaml.Media import MicaBackdrop
from win32more.Windows.ApplicationModel.DataTransfer import DataPackageOperation
from win32more.Windows.Foundation import AsyncStatus
from win32more.Windows.Foundation.Collections import IVector
from win32more.Windows.Graphics import PointInt32, SizeInt32

from toga import App
from toga.command import Group, Separator
from toga.constants import TRANSPARENT, WindowState
from toga.handlers import WeakrefCallable
from toga.types import Position, Size

from .colors import native_brush
from .container import Container
from .libs.misc import column_definition_star, row_definition_auto, row_definition_star
from .libs.screenshot import capture_client
from .screens import Screen as ScreenImpl

if TYPE_CHECKING:  # pragma: no cover
    from toga.types import PositionT, SizeT


class Window:
    def __init__(self, interface, title, position, size):
        self.interface = interface

        self.is_activated = False
        self.create()

        self._set_restrictions()
        self.set_title(title)
        self.set_size(size)

        # Use default behavior for position, rather than Toga's re-implementation.
        if position:
            self.set_position(position)

        # Create the window content and attach it.
        self.create_content()
        self.native.Content = self.content_native

    def create(self):
        self.native = App.app._impl.native_instance.CreateWindow()
        self.native.SystemBackdrop = MicaBackdrop()
        self.native.AppWindow.TitleBar.PreferredTheme = TitleBarTheme.UseDefaultAppMode
        self._programmatic_close = False
        self._cached_window_size = None
        self._restore_window_size = None
        self._fullscreen_reported_size = None
        self._in_fullscreen_mode = False
        self._in_presentation_mode = False
        self._previous_state = WindowState.NORMAL
        self._drop_operations = []

        self.native.Activated += WeakrefCallable(self.native_event_activated)
        self.native.AppWindow.Changed += WeakrefCallable(self.native_event_changed)
        self.native.AppWindow.Closing += WeakrefCallable(self.native_event_closing)

    def create_content(self):
        """Construct the container."""
        self.content_native = Canvas()
        self._enable_file_drop(self.content_native)
        self.container = Container(
            self.content_native,
            on_refresh=self.content_refreshed,
        )

    def _set_restrictions(self):
        """Sets the window properties of being minimizable and resizable."""
        overlapped_presenter = self._overlapped_presenter()
        if overlapped_presenter is None:
            return

        overlapped_presenter.IsMinimizable = self.interface.minimizable
        overlapped_presenter.IsResizable = self.interface.resizable

    def _overlapped_presenter(self):
        presenter = self.native.AppWindow.Presenter
        if presenter.Kind != AppWindowPresenterKind.Overlapped:
            return None

        return presenter.as_(OverlappedPresenter)

    def _set_window_chrome_visible(self, visible):
        pass

    def _enter_fullscreen_like_state(self, presentation=False):
        presenter = self._overlapped_presenter()
        current_state = self.get_window_state()
        self._restore_window_size = self.get_size()
        if current_state in {WindowState.MINIMIZED, WindowState.MAXIMIZED}:
            presenter.Restore()

        if presentation:
            if not hasattr(self, "_before_presentation_mode_screen"):
                self._before_presentation_mode_screen = self.interface.screen
            self._set_window_chrome_visible(False)
            self._in_presentation_mode = True
        else:
            self._in_fullscreen_mode = True
            presenter.Maximize()
            # Native fullscreen reports client-style bounds, while maximized and
            # presentation report overlapped-window bounds. Keep Toga's logical
            # Window.size comparable across state transitions.
            self._fullscreen_reported_size = self._appwindow_size()
            self.native.AppWindow.SetPresenterByKind(AppWindowPresenterKind.FullScreen)
            return

        presenter.Maximize()

    def _exit_fullscreen_like_state(self):
        if self._in_presentation_mode:
            self._set_window_chrome_visible(True)
            self.interface.screen = self._before_presentation_mode_screen
            del self._before_presentation_mode_screen

        self._in_fullscreen_mode = False
        self._in_presentation_mode = False
        self._fullscreen_reported_size = None

        if self.native.AppWindow.Presenter.Kind == AppWindowPresenterKind.FullScreen:
            self.native.AppWindow.SetPresenterByKind(AppWindowPresenterKind.Overlapped)

        presenter = self._overlapped_presenter()
        presenter.Restore()
        if self._restore_window_size is not None:
            restore_window_size = self._restore_window_size
            self._restore_window_size = None
            self.set_size(restore_window_size)

    ####################################################################################
    # Native event handlers.
    ####################################################################################

    def native_event_activated(self, sender, args):
        """Event that fires when the window is activated or deactivated."""
        # learn.microsoft.com/windows/windows-app-sdk/api/winrt/microsoft.ui.xaml.window.activated # noqa: E501
        if self.interface is None:
            return

        if args.WindowActivationState == WindowActivationState.Deactivated:
            self.is_activated = False
            self.interface.on_lose_focus()
        else:
            self.is_activated = True
            self.interface.app._impl._current_window = self
            self.interface.on_gain_focus()

    def native_event_changed(self, sender, args):
        if self.interface is None:
            return

        current_state = self.get_window_state(in_progress_state=True)
        if args.DidSizeChange:
            if {self._previous_state, current_state} != {
                WindowState.NORMAL,
                WindowState.MINIMIZED,
            }:
                self._cached_window_size = self._appwindow_size()
                self.interface.on_resize()

        if args.DidVisibilityChange:
            if self.native.AppWindow.IsVisible:
                self.interface.on_show()
            else:
                if self.interface.app._impl._current_window is self:
                    self.interface.app._impl._current_window = None
                self.interface.on_hide()

        if args.DidPresenterChange:
            if self._previous_state != current_state:
                if self._previous_state == WindowState.MINIMIZED:
                    self.interface.on_show()
                elif current_state == WindowState.MINIMIZED:
                    self.interface.on_hide()

            self._set_restrictions()
            self._previous_state = current_state

    def native_event_closing(self, sender, args):
        if self.interface is None:
            return

        if self._programmatic_close or self.interface.app._impl._is_exiting:
            return

        args.Cancel = True
        if self.interface.closable:
            self.interface.on_close()

    def native_event_drag_over(self, sender, args):
        if self.interface and self.interface.app.documents.types:
            args.AcceptedOperation = DataPackageOperation.Copy
        else:
            args.AcceptedOperation = DataPackageOperation.None_
        args.Handled = True

    def native_event_drop(self, sender, args):
        if self.interface is None or not self.interface.app.documents.types:
            return

        args.AcceptedOperation = DataPackageOperation.Copy
        args.Handled = True

        operation = args.DataView.GetStorageItemsAsync()
        self._drop_operations.append(operation)

        def completed(async_info, async_status):
            try:
                if async_status == AsyncStatus.Completed and self.interface is not None:
                    paths = self._paths_from_storage_items(async_info.GetResults())
                    self.interface.app.loop.call_soon_threadsafe(
                        self.open_dropped_files,
                        paths,
                    )
            finally:
                if operation in self._drop_operations:
                    self._drop_operations.remove(operation)

        operation.Completed = completed

    def _paths_from_storage_items(self, items):
        paths = []
        for item in items:
            if path := getattr(item, "Path", None):
                paths.append(Path(path))
        return paths

    def _enable_file_drop(self, native):
        native.AllowDrop = True
        if hasattr(native, "Background") and native.Background is None:
            native.Background = native_brush(TRANSPARENT)
        native.DragOver += WeakrefCallable(self.native_event_drag_over)
        native.Drop += WeakrefCallable(self.native_event_drop)

    def open_dropped_files(self, paths):
        if self.interface is None:
            return

        for path in paths:
            self.interface.app._open_initial_document(path)

    ####################################################################################
    # Window properties
    ####################################################################################

    def get_title(self) -> str:
        """Gets the title of the window, i.e. the text on the title bar."""
        return self.native.AppWindow.Title

    def set_title(self, title: str):
        """Sets the title of the window, i.e. the text on the title bar."""
        self.native.AppWindow.Title = title

    ####################################################################################
    # Window lifecycle
    ####################################################################################

    def close(self):
        if self.native is None or self.native.AppWindow is None:
            return

        interface = self.interface
        self._programmatic_close = True
        if interface is not None and interface.app._impl._current_window is self:
            interface.app._impl._current_window = None
        if self.container is not None:
            self.container.content = None
            self.container.on_refresh = None
        self.interface = None
        self.native.Content = None
        self.native.Close()
        self.is_activated = False
        self.container = None
        self.content_native = None
        self.native = None

    def set_app(self, app):
        """Sets the window icon to be the icon associated to the given app."""
        self.set_icon(app.interface.icon)

    def set_icon(self, icon):
        self.icon = icon
        self.native.AppWindow.SetIconWithIconId(icon._impl.id)

    def show(self):
        if self.interface.content is not None:
            self.interface.content.refresh()

        self.native.AppWindow.Show()
        self.interface.app._impl._current_window = self
        self.native.Activate()
        if self.interface.content is not None:
            bounds = self.native.Bounds
            if bounds.Width and bounds.Height:
                self.container.native.Width = bounds.Width
                self.container.native.Height = bounds.Height

            self.interface.content.refresh()

            if bounds.Width and bounds.Height:
                self.container.native.Width = float("nan")
                self.container.native.Height = float("nan")

    ####################################################################################
    # Window content and resources.
    ####################################################################################

    def content_refreshed(self, container):
        if self.interface is None or self.interface.content is None:
            return
        if self.get_window_state() in {
            WindowState.FULLSCREEN,
            WindowState.PRESENTATION,
        }:
            return

        min_width = self.interface.content.layout.min_width
        min_height = self.interface.content.layout.min_height
        size = self.get_size()
        extra_width = max(0, size.width - container.width)
        extra_height = max(0, size.height - container.height)

        width = max(size.width, min_width + extra_width)
        height = max(size.height, min_height + extra_height)
        if (width, height) != size:
            self.set_size((width, height))

    def set_content(self, widget):
        """Sets the content of the window's container to be the given Toga widget."""
        self.container.content = widget

    ####################################################################################
    # Window size (CSS pixels).
    #
    # Toga terminology <-> Microsoft terminology:
    #   - Physical pixels <-> Device pixels
    #       - The individual physical pixels that comprise the screen.
    #   - CSS pixels <-> Effective pixels ()
    #       - A virtual unit of measurement used for internal window properties so that
    #         a window appears the on screens with different scale factors.
    #
    # Example: For a 200% scale factor 1 css pixel is a 2x2 block of physical pixels.
    ####################################################################################

    def get_size(self) -> Size:
        """Gets the outer size of the window in effective pixels (CSS pixels)."""
        state = self.get_window_state()
        if state == WindowState.MINIMIZED:
            return self._cached_window_size
        elif state == WindowState.FULLSCREEN and self._fullscreen_reported_size:
            return self._fullscreen_reported_size

        return self._appwindow_size()

    def _appwindow_size(self):
        pixels_to_css = self.get_current_screen().pixels_to_css
        size = self.native.AppWindow.Size
        return Size(
            pixels_to_css(size.Width),
            pixels_to_css(size.Height),
        )

    def set_size(self, size: SizeT):
        """Sets the size of the window in effective pixels (CSS pixels)."""
        self._cached_window_size = Size(*size)
        pixels_to_physical = self.get_current_screen().pixels_to_physical

        self.native.AppWindow.Resize(
            SizeInt32(pixels_to_physical(size[0]), pixels_to_physical(size[1]))
        )

    ####################################################################################
    # Window position (CSS pixels, see window size for terminology).
    ####################################################################################

    def get_current_screen(self):
        return ScreenImpl(
            DisplayArea.GetFromWindowId(
                self.native.AppWindow.Id,
                DisplayAreaFallback.Primary,
            )
        )

    # Window.position is scaled according to the DPI of the primary screen so it remains
    # comparable with the cross-platform Screen origin and Window screen-position
    # contract.
    def get_position(self) -> Position:
        position = self.native.AppWindow.Position
        pixels_to_css = App.app._impl.get_primary_screen().pixels_to_css

        return Position(pixels_to_css(position.X), pixels_to_css(position.Y))

    def set_position(self, position: PositionT):
        pixels_to_physical = App.app._impl.get_primary_screen().pixels_to_physical

        self.native.AppWindow.Move(
            PointInt32(pixels_to_physical(position.x), pixels_to_physical(position.y))
        )

    ####################################################################################
    # Window visibility.
    ####################################################################################

    def get_visible(self) -> bool:
        """Returns True if the window is visible and False otherwise."""
        if self.native is None or self.native.AppWindow is None:
            return False
        return self.native.AppWindow.IsVisible

    def hide(self):
        """Hides but does not destroy the window."""
        if self.interface.app._impl._current_window is self:
            self.interface.app._impl._current_window = None
        self.native.AppWindow.Hide()

    ####################################################################################
    # Window state.
    ####################################################################################

    def get_window_state(self, in_progress_state=False) -> WindowState:
        """Gets the current state of the window.

        :param in_progress_state: Not supported on WinUI 3.
        :return: A WindowState constant determined by NORMAL, MAXIMIZED, MINIMIZED or
            FULLSCREEN or PRESENTATION.
        """
        presenter = self.native.AppWindow.Presenter

        if self._in_presentation_mode:
            # Presentation is currently modeled as a maximized overlapped window with
            # Toga app chrome hidden.
            return WindowState.PRESENTATION
        elif self._in_fullscreen_mode:
            return WindowState.FULLSCREEN
        elif presenter.Kind == AppWindowPresenterKind.FullScreen:
            return WindowState.FULLSCREEN
        else:
            # Assume presenter.Kind == AppWindowPresenterKind.Overlapped, since the
            # third alternative 'CompactOverlay' is not implemented by Toga.
            # learn.microsoft.com/en-us/windows/apps/develop/ui/manage-app-windows
            overlapped_presenter = self._overlapped_presenter()

            if overlapped_presenter.State == OverlappedPresenterState.Maximized:
                return WindowState.MAXIMIZED
            elif overlapped_presenter.State == OverlappedPresenterState.Minimized:
                return WindowState.MINIMIZED
            else:
                return WindowState.NORMAL

    def set_window_state(self, state: WindowState):
        """Sets the state of the window.

        :state: A WindowState constant determined by NORMAL, MAXIMIZED, MINIMIZED or
            PRESENTATION.
        """
        if state != WindowState.PRESENTATION and any(
            window.state == WindowState.PRESENTATION
            for window in self.interface.app.windows
            if window != self.interface
        ):
            self.interface.app.exit_presentation_mode()

        current_state = self.get_window_state()

        if state == current_state:
            return
        show_on_restore = (
            current_state == WindowState.MINIMIZED and state == WindowState.NORMAL
        )
        resize_expected = (current_state != state) and not (
            {current_state, state} == {WindowState.NORMAL, WindowState.MINIMIZED}
        )

        if current_state in {WindowState.FULLSCREEN, WindowState.PRESENTATION}:
            self._exit_fullscreen_like_state()
            if state != WindowState.NORMAL:
                self.set_window_state(state)
            if show_on_restore:
                self.interface.on_show()
            if resize_expected:
                self.interface.on_resize()
            return

        if state == WindowState.FULLSCREEN:
            self._enter_fullscreen_like_state()
            if show_on_restore:
                self.interface.on_show()
            if resize_expected:
                self.interface.on_resize()
            return
        elif state == WindowState.PRESENTATION:
            self._enter_fullscreen_like_state(presentation=True)
            if show_on_restore:
                self.interface.on_show()
            if resize_expected:
                self.interface.on_resize()
            return

        match state:
            case WindowState.NORMAL:
                self._overlapped_presenter().Restore()

            case WindowState.MINIMIZED:
                self._overlapped_presenter().Minimize()

            case _:
                self._overlapped_presenter().Maximize()

        if show_on_restore:
            self.interface.on_show()
        if resize_expected:
            self.interface.on_resize()

    ####################################################################################
    # Window capabilities
    ####################################################################################

    def get_image_data(self):
        hwnd = GetWindowFromWindowId(self.native.AppWindow.Id)
        return capture_client(hwnd)


class MainWindow(Window):
    def create(self):
        super().create()
        self.toolbar_native = None
        self.toolbar_commands = []
        self.window_menu_actions = []

    def _set_window_chrome_visible(self, visible):
        visibility = Visibility.Visible if visible else Visibility.Collapsed
        if hasattr(self, "menu_native"):
            self.menu_native.Visibility = visibility
        if self.toolbar_native:
            self.toolbar_native.Visibility = visibility

    def create_content(self):
        # Row 0 is allocated for the menu
        # Row 1 is allocated for toolbar
        self.content_native = Grid()
        self._enable_file_drop(self.content_native)
        self.content_native.ColumnDefinitions.Append(column_definition_star(1))
        self.content_native.RowDefinitions.Append(row_definition_auto())
        self.content_native.RowDefinitions.Append(row_definition_auto())
        self.content_native.RowDefinitions.Append(row_definition_star(1))

        self.content_native.HorizontalAlignment = HorizontalAlignment.Stretch
        self.content_native.VerticalAlignment = VerticalAlignment.Stretch

        self.container_native = Canvas()
        self._enable_file_drop(self.container_native)
        Grid.SetRow(self.container_native, 2)
        Grid.SetColumn(self.container_native, 0)
        self.content_native.Children.Append(self.container_native)

        self.container = Container(
            self.container_native,
            on_refresh=self.content_refreshed,
        )

        # Attach the content to the window.
        self.native.Content = self.content_native

    def _submenu(self, group, group_cache):
        try:
            return group_cache[group]
        except KeyError:
            parent_menu = self._submenu(group.parent, group_cache)

            # If group.parent is None, then parent_menu is the MenuBar instance and the
            # type of items that can be added are MenuBarItem. Otherwise, parent_menu is
            # of type MenuBarItem or of type MenuFlyoutSubItem and submenus are added
            # with MenuFlyoutSubItem.
            if group.parent is None:
                submenu = MenuBarItem()
                submenu.Title = group.text
            else:
                submenu = MenuFlyoutSubItem()
                submenu.Text = group.text

            parent_menu.Items.Append(submenu)

            group_cache[group] = submenu
        return submenu

    def create_menus(self):
        self.menu_native = MenuBar()
        self.menu_native.VerticalAlignment = VerticalAlignment.Top
        Grid.SetRow(self.menu_native, 0)
        Grid.SetColumn(self.menu_native, 0)
        self.window_menu_actions = []

        group_cache = {None: self.menu_native}

        submenu = None
        for cmd in self.interface.app.commands:
            submenu = self._submenu(cmd.group, group_cache)
            if isinstance(cmd, Separator):
                item = MenuFlyoutSeparator()
            else:
                item = cmd._impl.create_menu_item(MenuFlyoutItem)

            submenu.Items.Append(item)

        self._create_window_management_menus(group_cache)

        self.content_native.Children.Append(self.menu_native)

    def _add_window_menu_item(self, submenu, text, action, event_handler):
        item = MenuFlyoutItem()
        item.Text = text
        item.add_Click(WeakrefCallable(event_handler))
        submenu.Items.Append(item)
        self.window_menu_actions.append((item, action))

    def _create_window_management_menus(self, group_cache):
        file_menu = self._submenu(Group.FILE, group_cache)
        file_menu.Items.Append(MenuFlyoutSeparator())
        self._add_window_menu_item(
            file_menu,
            "Close",
            self.close_current_window,
            self.native_event_close_current_window,
        )
        self._add_window_menu_item(
            file_menu,
            "Close All",
            self.close_all_windows,
            self.native_event_close_all_windows,
        )

        window_menu = self._submenu(Group.WINDOW, group_cache)
        self._add_window_menu_item(
            window_menu,
            "Minimize",
            self.minimize_current_window,
            self.native_event_minimize_current_window,
        )

    def close_current_window(self):
        if window := self.interface.app.current_window:
            window.close()

    def close_all_windows(self):
        for window in list(self.interface.app.windows):
            window.close()

    def minimize_current_window(self):
        if window := self.interface.app.current_window:
            window.state = WindowState.MINIMIZED

    def native_event_close_current_window(self, sender, args):
        self.close_current_window()

    def native_event_close_all_windows(self, sender, args):
        self.close_all_windows()

    def native_event_minimize_current_window(self, sender, args):
        self.minimize_current_window()

    def create_toolbar(self):
        if self.interface.toolbar:
            self.toolbar_commands = []
            if self.toolbar_native:
                primary_commands = self.toolbar_native.PrimaryCommands.as_(
                    IVector[ICommandBarElement]
                )
                primary_commands.Clear()
            else:
                self.toolbar_native = CommandBar()
                self.toolbar_native.IsDynamicOverflowEnabled = False
                self.toolbar_native.DefaultLabelPosition = (
                    CommandBarDefaultLabelPosition.Right
                )
                self.toolbar_native.HorizontalAlignment = HorizontalAlignment.Stretch
                self.toolbar_native.VerticalAlignment = VerticalAlignment.Top
                Grid.SetRow(self.toolbar_native, 1)
                Grid.SetColumn(self.toolbar_native, 0)
                self.content_native.Children.Append(self.toolbar_native)
                primary_commands = self.toolbar_native.PrimaryCommands.as_(
                    IVector[ICommandBarElement]
                )

            prev_group = None
            for cmd in self.interface.toolbar:
                if isinstance(cmd, Separator):
                    item = AppBarSeparator()
                    prev_group = None
                else:
                    if prev_group is not None and prev_group != cmd.group:
                        primary_commands.Append(AppBarSeparator())
                        self.toolbar_commands.append(None)
                        prev_group = None
                    else:
                        prev_group = cmd.group

                    item = AppBarButton()
                    item.Label = cmd.text
                    if cmd.tooltip is not None:
                        ToolTipService.SetToolTip(item, cmd.tooltip)
                    if cmd.icon is not None:
                        icon = ImageIcon()
                        icon.Source = cmd.icon._impl.bitmap_image(32)
                        item.Icon = icon
                    item.IsEnabled = cmd.enabled
                    item.add_Click(cmd._impl.native_event_Click)
                    cmd._impl.native.append(item)
                    self.toolbar_commands.append(cmd)

                if isinstance(cmd, Separator):
                    self.toolbar_commands.append(None)
                primary_commands.Append(item)
        elif self.toolbar_native:
            index = UInt32()
            if self.content_native.Children.IndexOf(self.toolbar_native, byref(index)):
                self.content_native.Children.RemoveAt(index.value)
            self.toolbar_native = None
            self.toolbar_commands = []
            return
