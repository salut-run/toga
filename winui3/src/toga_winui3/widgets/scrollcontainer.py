from math import isfinite
from weakref import ref

from win32more.Microsoft.UI.Xaml.Controls import (
    Canvas,
    ScrollBarVisibility,
    ScrollMode,
    ScrollViewer,
)

from toga.handlers import WeakrefCallable
from toga_winui3.container import Container

from .base import Widget


class ScrollContentContainer(Container):
    def __init__(self, owner, native_panel):
        self._owner_ref = ref(owner)
        super().__init__(native_panel)

    @property
    def width(self):
        return round(self._owner._layout_width)

    @property
    def height(self):
        return round(self._owner._layout_height)

    def refreshed(self):
        if owner := self._owner_ref():
            owner.refreshed()

    @property
    def _owner(self):
        return self._owner_ref()


class ScrollContainer(Widget):
    def create(self):
        self.native = ScrollViewer()
        self.native_content = Canvas()
        self.native.Content = self.native_content
        self.native.ViewChanged += WeakrefCallable(self.native_event_view_changed)

        self.content_container = ScrollContentContainer(self, self.native_content)

        self._horizontal = True
        self._vertical = True
        self._horizontal_position = 0
        self._vertical_position = 0
        self._layout_width = 0
        self._layout_height = 0
        self._update_scroll_modes()

    def set_bounds(self, x, y, width, height):
        super().set_bounds(x, y, width, height)
        self._layout_width = width
        self._layout_height = height
        if self.content:
            self.content.interface.refresh()

    @property
    def content(self):
        return self.content_container.content

    def set_content(self, widget):
        self.content_container.content = widget
        self.refreshed()

    def get_horizontal(self):
        return self._horizontal

    def set_horizontal(self, value):
        self._horizontal = value
        self._update_scroll_modes()
        if not value:
            self.set_position(0, self._vertical_position)
        elif self.content:
            self.content.interface.refresh()

    def get_vertical(self):
        return self._vertical

    def set_vertical(self, value):
        self._vertical = value
        self._update_scroll_modes()
        if not value:
            self.set_position(self._horizontal_position, 0)
        elif self.content:
            self.content.interface.refresh()

    def get_horizontal_position(self):
        if not self._horizontal:
            return 0

        return round(self._horizontal_position)

    def get_vertical_position(self):
        if not self._vertical:
            return 0

        return round(self._vertical_position)

    def get_max_horizontal_position(self):
        if not self._horizontal:
            return 0

        return round(max(0, self._document_width - self._viewport_width))

    def get_max_vertical_position(self):
        if not self._vertical:
            return 0

        return round(max(0, self._document_height - self._viewport_height))

    def set_position(self, horizontal_position, vertical_position):
        horizontal_position = 0 if not self._horizontal else horizontal_position
        vertical_position = 0 if not self._vertical else vertical_position

        self._horizontal_position = horizontal_position
        self._vertical_position = vertical_position

        self.native.ScrollToHorizontalOffset(horizontal_position)
        self.native.ScrollToVerticalOffset(vertical_position)
        self.interface.on_scroll()

    def refreshed(self):
        content = self.content
        if content is None:
            return

        layout = content.interface.layout
        self.native_content.Width = max(
            self._viewport_width,
            layout.width if self._horizontal else self._viewport_width,
        )
        self.native_content.Height = max(
            self._viewport_height,
            layout.height if self._vertical else self._viewport_height,
        )

        horizontal_position = min(
            self._horizontal_position,
            self.get_max_horizontal_position(),
        )
        vertical_position = min(
            self._vertical_position,
            self.get_max_vertical_position(),
        )
        if (
            horizontal_position != self._horizontal_position
            or vertical_position != self._vertical_position
        ):
            self.set_position(horizontal_position, vertical_position)

    def native_event_view_changed(self, sender, args):
        self._horizontal_position = self.native.HorizontalOffset
        self._vertical_position = self.native.VerticalOffset
        self.interface.on_scroll()

    def _update_scroll_modes(self):
        self.native.HorizontalScrollMode = (
            ScrollMode.Enabled if self._horizontal else ScrollMode.Disabled
        )
        self.native.HorizontalScrollBarVisibility = (
            ScrollBarVisibility.Auto
            if self._horizontal
            else ScrollBarVisibility.Disabled
        )
        self.native.VerticalScrollMode = (
            ScrollMode.Enabled if self._vertical else ScrollMode.Disabled
        )
        self.native.VerticalScrollBarVisibility = (
            ScrollBarVisibility.Auto if self._vertical else ScrollBarVisibility.Disabled
        )

    @property
    def _viewport_width(self):
        if self._layout_width:
            return self._layout_width
        if isfinite(self.native.ViewportWidth) and self.native.ViewportWidth:
            return self.native.ViewportWidth
        if self.native.ActualSize.X:
            return self.native.ActualSize.X
        if isfinite(self.native.Width):
            return self.native.Width
        return 0

    @property
    def _viewport_height(self):
        if self._layout_height:
            return self._layout_height
        if isfinite(self.native.ViewportHeight) and self.native.ViewportHeight:
            return self.native.ViewportHeight
        if self.native.ActualSize.Y:
            return self.native.ActualSize.Y
        if isfinite(self.native.Height):
            return self.native.Height
        return 0

    @property
    def _document_width(self):
        if isfinite(self.native_content.Width):
            return self.native_content.Width
        return 0

    @property
    def _document_height(self):
        if isfinite(self.native_content.Height):
            return self.native_content.Height
        return 0
