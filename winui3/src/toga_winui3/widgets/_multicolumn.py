from dataclasses import dataclass

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import (
    Grid,
    Image as NativeImage,
    ListView,
    ListViewItem,
    ListViewSelectionMode,
    Orientation,
    StackPanel,
    TextBlock,
)
from win32more.Microsoft.UI.Xaml.Media import Stretch

from ..libs.misc import row_definition_auto, row_definition_star
from .base import Widget

DEFAULT_COLUMN_WIDTH = 120
ICON_SIZE = 16


@dataclass
class CellValue:
    text: str | None
    icon: object | None = None
    widget: object | None = None


class MulticolumnListView(Widget):
    """Shared native presentation for Table and Tree."""

    def create(self):
        self.native = Grid()
        self.header = StackPanel()
        self.header.Orientation = Orientation.Horizontal
        self.list_view = ListView()
        self.list_view.IsTabStop = True
        self.list_view.SelectionMode = (
            ListViewSelectionMode.Multiple
            if self.interface.multiple_select
            else ListViewSelectionMode.Single
        )
        self.native.RowDefinitions.Append(row_definition_auto())
        self.native.RowDefinitions.Append(row_definition_star(1))
        Grid.SetRow(self.header, 0)
        Grid.SetRow(self.list_view, 1)
        self.native.Children.Append(self.header)
        self.native.Children.Append(self.list_view)

        self._column_widths = [
            DEFAULT_COLUMN_WIDTH for _column in self.interface.columns
        ]
        self._manual_column_widths = False
        self._selection = [] if self.interface.multiple_select else None
        self._scroll_row = 0
        self._width = 0
        self._last_layout_width = 0
        self._initialize_data_state()
        self._update_header()

    def _initialize_data_state(self):
        self._row_cache = []

    @property
    def _columns(self):
        return self.interface.columns

    @property
    def _data(self):
        return self.interface.data

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def _focus_target(self):
        return self.list_view

    def set_font(self, font):
        super().set_font(font)
        self._apply_font(self.list_view)

    def insert_column(self, index, column):
        self._column_widths.insert(index, self._default_column_width())
        self._columns_changed()
        self._resize_columns()

    def remove_column(self, index):
        del self._column_widths[index]
        self._columns_changed()
        self._resize_columns()

    def _columns_changed(self):
        raise NotImplementedError

    def get_selection(self):
        if self.interface.multiple_select:
            return list(self._selection)
        return self._selection

    def scroll_to_row(self, index):
        self._scroll_row = max(0, min(index, max(self._row_count - 1, 0)))
        if len(self.list_view.Items):
            self.list_view.ScrollIntoView(self.list_view.Items.GetAt(self._scroll_row))

    @property
    def _row_count(self):
        return len(self._data)

    def set_bounds(self, x, y, width, height):
        super().set_bounds(x, y, width, height)
        self._width = width
        self._resize_columns()

    def _default_column_width(self):
        if self._column_widths:
            return sum(self._column_widths) / len(self._column_widths)
        return DEFAULT_COLUMN_WIDTH

    def _resize_columns(self):
        column_count = len(self._column_widths)
        if column_count == 0:
            return

        if self._manual_column_widths:
            if self._width and self._last_layout_width != self._width:
                scale = self._width / self._last_layout_width
                self._column_widths = [width * scale for width in self._column_widths]
                self._last_layout_width = self._width
        elif self._width:
            width = self._width / column_count
            self._column_widths = [width for _column in self._column_widths]
            self._last_layout_width = self._width

        self._update_header()
        self._sync_native_rows()

    def resize_column(self, index, width):
        self._manual_column_widths = True
        self._last_layout_width = self._width
        self._column_widths[index] = width
        self._update_header()
        self._sync_native_rows()

    def _update_header(self):
        self.header.Children.Clear()
        self.header.Visibility = 0 if self.interface.show_headings else 1

        if self.interface.show_headings:
            for column, width in zip(
                self._columns,
                self._column_widths,
                strict=False,
            ):
                text = TextBlock()
                text.Text = column.heading
                text.Width = width
                self.header.Children.Append(text)

    def _row_values(self, row):
        values = []
        for column in self._columns:
            if widget := column.widget(row):
                values.append(CellValue(None, widget=widget))
            else:
                values.append(
                    CellValue(
                        column.text(row, self.interface.missing_value),
                        column.icon(row),
                    )
                )
        return values

    def _native_rows(self):
        return self._row_cache

    def _values_for_native_row(self, row):
        return row

    def _display_parts(self, row, index, value):
        return "", "" if value is None else str(value)

    def _native_row(self, row_state):
        item = ListViewItem()
        row = StackPanel()
        row.Orientation = Orientation.Horizontal

        values = self._values_for_native_row(row_state)
        for index, (value, width) in enumerate(
            zip(values, self._column_widths, strict=False)
        ):
            prefix, text = self._display_parts(row_state, index, value.text)
            row.Children.Append(
                self._native_cell(prefix, text, value.icon, value.widget, width)
            )

        item.Content = row
        return item

    def _native_cell(self, prefix, text, icon, widget, width):
        if widget is not None:
            return self._native_widget_cell(prefix, widget, width)

        if prefix == "" and icon is None:
            cell = TextBlock()
            cell.Text = text
            cell.Width = width
            return cell

        cell = StackPanel()
        cell.Orientation = Orientation.Horizontal
        cell.Width = width

        if prefix:
            prefix_block = TextBlock()
            prefix_block.Text = prefix
            cell.Children.Append(prefix_block)

        if icon is not None:
            image = NativeImage()
            image.Width = ICON_SIZE
            image.Height = ICON_SIZE
            image.Stretch = Stretch.Uniform
            image.Source = icon._impl.bitmap_image(ICON_SIZE)
            cell.Children.Append(image)

        text_block = TextBlock()
        text_block.Text = text
        cell.Children.Append(text_block)
        return cell

    def _native_widget_cell(self, prefix, widget, width):
        cell = StackPanel()
        cell.Orientation = Orientation.Horizontal
        cell.Width = width

        if prefix:
            prefix_block = TextBlock()
            prefix_block.Text = prefix
            cell.Children.Append(prefix_block)

        native = widget._impl.native
        self._detach_native(native)
        if hasattr(native, "Width"):
            native.Width = width
        cell.Children.Append(native)
        return cell

    def _detach_native(self, native):
        try:
            parent = native.Parent
        except (AttributeError, OSError, TypeError):
            return

        if parent is not None and hasattr(parent, "Children"):
            parent.Children.Remove(native)

    def _sync_native_rows(self):
        rows = list(self._native_rows())
        self._row_cache = [self._values_for_native_row(row) for row in rows]
        self.list_view.Items.Clear()
        for row in rows:
            self.list_view.Items.Append(self._native_row(row))

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
