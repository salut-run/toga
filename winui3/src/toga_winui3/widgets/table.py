import warnings

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import (
    Grid,
    ListView,
    ListViewItem,
    ListViewSelectionMode,
    Orientation,
    StackPanel,
    TextBlock,
)

from toga.sources import ListListener
from toga_winui3.libs.misc import row_definition_auto, row_definition_star

from .base import Widget

ROW_HEIGHT = 32
DEFAULT_COLUMN_WIDTH = 120


class Table(Widget, ListListener):
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
        self._row_cache = []

        self._update_header()

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

    def change_source(self, source):
        self.update_data()

    def update_data(self):
        self._row_cache = [self._row_values(row) for row in self._data]
        self._sync_native_rows()
        self._coerce_selection()
        self.interface.refresh()

    def source_insert(self, *, index, item):
        self.update_data()

    def source_change(self, *, item):
        self.update_data()

    def source_remove(self, *, index, item):
        self.update_data()

    def source_clear(self):
        self.update_data()

    def insert_column(self, index, column):
        width = self._default_column_width()
        self._column_widths.insert(index, width)
        self.update_data()
        self._resize_columns()
        self._update_header()

    def remove_column(self, index):
        del self._column_widths[index]
        self.update_data()
        self._resize_columns()
        self._update_header()

    def get_selection(self):
        if self.interface.multiple_select:
            return list(self._selection)
        return self._selection

    def scroll_to_row(self, index):
        self._scroll_row = max(0, min(index, max(len(self._data) - 1, 0)))
        if len(self.list_view.Items):
            self.list_view.ScrollIntoView(self.list_view.Items.GetAt(self._scroll_row))

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
            if column.widget(row) is not None:
                warnings.warn(
                    "WinUI does not support the use of widgets in cells",
                    stacklevel=1,
                )
                values.append(self.interface.missing_value)
            else:
                values.append(column.text(row, self.interface.missing_value))
        return values

    def _native_row(self, values):
        item = ListViewItem()
        row = StackPanel()
        row.Orientation = Orientation.Horizontal
        for value, width in zip(values, self._column_widths, strict=False):
            cell = TextBlock()
            cell.Text = value
            cell.Width = width
            row.Children.Append(cell)
        item.Content = row
        return item

    def _sync_native_rows(self):
        self.list_view.Items.Clear()
        for values in self._row_cache:
            self.list_view.Items.Append(self._native_row(values))

    def _coerce_selection(self):
        row_count = len(self._data)
        if self.interface.multiple_select:
            self._selection = [row for row in self._selection if row < row_count]
        elif self._selection is not None and self._selection >= row_count:
            self._selection = None

    def select_row(self, row, add=False):
        if not len(self._data):
            return

        row = max(0, min(row, len(self._data) - 1))
        if self.interface.multiple_select:
            if add:
                if row in self._selection:
                    self._selection.remove(row)
                else:
                    self._selection.append(row)
                    self._selection.sort()
            else:
                self._selection = [row]
        else:
            self._selection = row

        self.interface.on_select()

    def select_first_row(self):
        if len(self._data):
            self.select_row(0)

    def select_next_row(self, add=False):
        if not len(self._data):
            return

        if self.interface.multiple_select:
            current = max(self._selection, default=-1)
        else:
            current = -1 if self._selection is None else self._selection
        self.select_row(min(current + 1, len(self._data) - 1), add=add)

    def select_previous_row(self, add=False):
        if not len(self._data):
            return

        if self.interface.multiple_select:
            if add and self._selection:
                self._selection.pop()
                self.interface.on_select()
                return
            current = min(self._selection, default=1)
        else:
            current = 0 if self._selection is None else self._selection
        self.select_row(max(current - 1, 0), add=add)

    def activate_row(self, row):
        self.select_row(row)
        self.interface.on_activate(row=self._data[row])

    # Alias for backwards compatibility:
    # March 2026: In 0.5.3 and earlier, notification methods
    # didn't start with 'source_'
    def clear(self):
        warnings.warn(
            "The clear() method is deprecated. Use source_clear() instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        self.source_clear()

    def insert(self, index, item):
        warnings.warn(
            "The insert() method is deprecated. Use source_insert() instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        self.source_insert(index=index, item=item)

    def change(self, item):
        warnings.warn(
            "The change() method is deprecated. Use source_change() instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        self.source_change(item=item)

    def remove(self, index, item):
        warnings.warn(
            "The remove() method is deprecated. Use source_remove() instead.",
            DeprecationWarning,
            stacklevel=1,
        )
        self.source_remove(index=index, item=item)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
