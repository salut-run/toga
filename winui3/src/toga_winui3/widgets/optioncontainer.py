from math import isfinite
from weakref import ref

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import (
    Canvas,
    TabView,
    TabViewItem,
    TabViewWidthMode,
    TextBlock,
)

from toga.handlers import WeakrefCallable
from toga_winui3.container import Container

from .base import Widget

TAB_CHROME_HEIGHT = 48


def int_value(value):
    return int(getattr(value, "value", value))


class OptionPaneContainer(Container):
    def __init__(self, native_panel, owner):
        super().__init__(native_panel)
        self.owner = ref(owner)
        self.min_width = 0
        self.min_height = 0

    def refreshed(self):
        if owner := self.owner():
            owner.content_refreshed(self)


class OptionContainer(Widget):
    uses_icons = False

    def create(self):
        self.native = TabView()
        self.native.IsAddTabButtonVisible = False
        self.native.CanDragTabs = False
        self.native.AllowDropTabs = False
        self.native.TabWidthMode = TabViewWidthMode.SizeToContent
        self.native.SelectionChanged += WeakrefCallable(
            self.native_event_selection_changed
        )

        self.tabs = []
        self.containers = []
        self._width = None
        self._height = None
        self._current_index = None

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def has_focus(self):
        return False

    def focus(self):
        pass

    def native_event_selection_changed(self, sender, args):
        index = self.get_current_tab_index()
        self._refresh_current_tab()
        if index != self._current_index:
            self._current_index = index
            self.interface.on_select()

    def add_option(self, index, text, widget, icon):
        panel = Canvas()
        container = OptionPaneContainer(panel, self)
        container.content = widget

        tab = TabViewItem()
        tab.Header = self._create_header(text)
        tab.Content = panel
        tab.IsClosable = False

        self.tabs.insert(index, tab)
        self.containers.insert(index, container)
        self.native.TabItems.InsertAt(index, tab)

        if len(self.tabs) == 1:
            self._current_index = 0
            self.native.SelectedIndex = 0

        self._refresh_tabs(force_refresh=True)

    def remove_option(self, index):
        self.native.TabItems.RemoveAt(index)
        container = self.containers.pop(index)
        container.content = None
        del self.tabs[index]
        self._refresh_tabs(force_refresh=True)

    def set_option_enabled(self, index, enabled):
        self.tabs[index].IsEnabled = enabled

    def is_option_enabled(self, index):
        return self.tabs[index].IsEnabled

    def set_option_text(self, index, value):
        self.tabs[index].Header = self._create_header(value)

    def get_option_text(self, index):
        return self.tabs[index].Header.as_(TextBlock).Text

    def set_option_icon(self, index, value):
        pass

    def get_option_icon(self, index):
        return None

    def get_current_tab_index(self):
        index = int_value(self.native.SelectedIndex)
        return None if index == -1 else index

    def set_current_tab_index(self, current_tab_index):
        self.native.SelectedIndex = current_tab_index

    def set_bounds(self, x, y, width, height):
        super().set_bounds(x, y, width, height)
        self._width = width
        self._height = height
        self._refresh_tabs(force_refresh=True)

    def content_refreshed(self, container):
        if container.content:
            container.min_width = container.content.interface.layout.min_width
            container.min_height = container.content.interface.layout.min_height

        old_intrinsic = (
            self.interface.intrinsic.width,
            self.interface.intrinsic.height,
        )
        self.rehint()
        new_intrinsic = (
            self.interface.intrinsic.width,
            self.interface.intrinsic.height,
        )
        if old_intrinsic != new_intrinsic:
            self.interface.refresh()

    def _create_header(self, text):
        header = TextBlock()
        header.Text = text
        return header

    def _finite_extent(self, *values):
        for value in values:
            if value is not None and isfinite(value) and value > 0:
                return value
        return 0

    def _content_size(self):
        width = self._finite_extent(
            self._width,
            self.native.Width,
            self.native.ActualSize.X,
        )
        height = max(
            0,
            self._finite_extent(
                self._height,
                self.native.Height,
                self.native.ActualSize.Y,
            )
            - TAB_CHROME_HEIGHT,
        )
        return width, height

    def _refresh_tabs(self, force_refresh=False):
        width, height = self._content_size()
        for container in self.containers:
            panel = container.native
            panel.Width = width
            panel.Height = height
            container.assign_size(width, height)
            if force_refresh and container.content:
                container.content.interface.refresh()

    def _refresh_current_tab(self):
        index = self.get_current_tab_index()
        if index is not None:
            container = self.containers[index]
            if container.content:
                container.content.interface.refresh()

    def rehint(self):
        content_width = max(
            [container.min_width for container in self.containers],
            default=0,
        )
        content_height = max(
            [container.min_height for container in self.containers],
            default=0,
        )
        self.interface.intrinsic.width = at_least(
            max(content_width, self.interface._MIN_WIDTH)
        )
        self.interface.intrinsic.height = at_least(
            max(content_height + TAB_CHROME_HEIGHT, self.interface._MIN_HEIGHT)
        )
