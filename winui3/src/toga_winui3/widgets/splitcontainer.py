from math import isfinite

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml import GridLength, GridUnitType
from win32more.Microsoft.UI.Xaml.Controls import (
    Canvas,
    ColumnDefinition,
    Grid,
    RowDefinition,
)
from win32more.Microsoft.UI.Xaml.Controls.Primitives import Thumb

from toga.constants import Direction
from toga.handlers import WeakrefCallable
from toga_winui3.container import Container

from .base import Widget

SPLITTER_SIZE = 4
MIN_PANE_SIZE = 60


class SplitContainer(Widget):
    def create(self):
        self.native = Grid()
        self.panels = [Canvas(), Canvas()]
        self.splitter = Thumb()
        self.splitter.Width = SPLITTER_SIZE
        self.splitter.Height = SPLITTER_SIZE
        self.splitter.DragDelta += WeakrefCallable(self.native_event_drag_delta)
        self.containers = [Container(panel) for panel in self.panels]
        self._direction = Direction.VERTICAL
        self._flex = [1, 1]
        self._pixel_position = None
        self._width = None
        self._height = None
        self._apply_grid()

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def has_focus(self):
        return False

    def focus(self):
        pass

    def set_content(self, content, flex):
        for container in self.containers:
            container.content = None

        self._flex = flex
        self._pixel_position = None

        for container, widget in zip(self.containers, content, strict=False):
            container.content = widget

        self._apply_grid()
        self._refresh_panes(force_refresh=True)

    def get_direction(self):
        return self._direction

    def set_direction(self, value):
        self._direction = value
        self._pixel_position = None
        self._apply_grid()
        self._refresh_panes(force_refresh=True)

    def set_split_position(self, position):
        extent = self._split_extent()

        if extent:
            position = max(0, min(position, extent - MIN_PANE_SIZE))

        self._pixel_position = position
        self._apply_grid()
        self._refresh_panes(force_refresh=True)

    def set_bounds(self, x, y, width, height):
        super().set_bounds(x, y, width, height)
        self._width = width
        self._height = height
        self._refresh_panes(force_refresh=True)

    def native_event_drag_delta(self, sender, args):
        current = self._current_position()
        delta = (
            args.HorizontalChange
            if self._direction == Direction.VERTICAL
            else args.VerticalChange
        )
        self.set_split_position(current + delta)

    def _current_position(self):
        if self._pixel_position is not None:
            return self._pixel_position

        extent = self._split_extent()
        if not extent:
            return 0

        return extent * self._flex[0] / sum(self._flex)

    def _finite_extent(self, *values):
        for value in values:
            if value is not None and isfinite(value) and value > 0:
                return value
        return 0

    def _layout_size(self):
        return (
            self._finite_extent(
                self._width,
                self.native.Width,
                self.native.ActualSize.X,
            ),
            self._finite_extent(
                self._height,
                self.native.Height,
                self.native.ActualSize.Y,
            ),
        )

    def _split_extent(self):
        width, height = self._layout_size()
        extent = width if self._direction == Direction.VERTICAL else height
        return max(0, extent - SPLITTER_SIZE)

    def _pane_sizes(self):
        width, height = self._layout_size()
        split_extent = self._split_extent()
        if split_extent <= 0:
            first = second = 0
        elif self._pixel_position is None:
            first = split_extent * self._flex[0] / sum(self._flex)
            second = split_extent - first
        else:
            first = max(0, min(self._pixel_position, split_extent - MIN_PANE_SIZE))
            second = split_extent - first

        if self._direction == Direction.VERTICAL:
            return (first, height), (second, height)
        else:
            return (width, first), (width, second)

    def _refresh_panes(self, force_refresh=False):
        sizes = self._pane_sizes()
        for panel, container, (width, height) in zip(
            self.panels,
            self.containers,
            sizes,
            strict=False,
        ):
            panel.Width = width
            panel.Height = height
            container.assign_size(width, height)
            if force_refresh and container.content:
                container.content.interface.refresh()

        width, height = self._layout_size()
        if self._direction == Direction.VERTICAL:
            self.splitter.Width = SPLITTER_SIZE
            self.splitter.Height = height
        else:
            self.splitter.Width = width
            self.splitter.Height = SPLITTER_SIZE

    def _grid_length(self, index):
        if index == 0 and self._pixel_position is not None:
            return GridLength(self._pixel_position, GridUnitType.Pixel)
        return GridLength(self._flex[index], GridUnitType.Star)

    def _column(self, width):
        column = ColumnDefinition()
        column.Width = width
        return column

    def _row(self, height):
        row = RowDefinition()
        row.Height = height
        return row

    def _apply_grid(self):
        self.native.Children.Clear()
        self.native.ColumnDefinitions.Clear()
        self.native.RowDefinitions.Clear()

        if self._direction == Direction.VERTICAL:
            self.native.RowDefinitions.Append(
                self._row(GridLength(1, GridUnitType.Star))
            )
            self.native.ColumnDefinitions.Append(self._column(self._grid_length(0)))
            self.native.ColumnDefinitions.Append(
                self._column(GridLength(SPLITTER_SIZE, GridUnitType.Pixel))
            )
            self.native.ColumnDefinitions.Append(self._column(self._grid_length(1)))

            Grid.SetRow(self.panels[0], 0)
            Grid.SetColumn(self.panels[0], 0)
            Grid.SetRow(self.splitter, 0)
            Grid.SetColumn(self.splitter, 1)
            Grid.SetRow(self.panels[1], 0)
            Grid.SetColumn(self.panels[1], 2)
            self.splitter.Width = SPLITTER_SIZE
            self.splitter.Height = self.native.Height
        else:
            self.native.ColumnDefinitions.Append(
                self._column(GridLength(1, GridUnitType.Star))
            )
            self.native.RowDefinitions.Append(self._row(self._grid_length(0)))
            self.native.RowDefinitions.Append(
                self._row(GridLength(SPLITTER_SIZE, GridUnitType.Pixel))
            )
            self.native.RowDefinitions.Append(self._row(self._grid_length(1)))

            Grid.SetColumn(self.panels[0], 0)
            Grid.SetRow(self.panels[0], 0)
            Grid.SetColumn(self.splitter, 0)
            Grid.SetRow(self.splitter, 1)
            Grid.SetColumn(self.panels[1], 0)
            Grid.SetRow(self.panels[1], 2)
            self.splitter.Width = self.native.Width
            self.splitter.Height = SPLITTER_SIZE

        self.native.Children.Append(self.panels[0])
        self.native.Children.Append(self.splitter)
        self.native.Children.Append(self.panels[1])

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
