import pytest
from win32more.Microsoft.UI.Xaml.Controls import Grid

from .base import SimpleProbe

ROW_HEIGHT = 32


class TableProbe(SimpleProbe):
    native_class = Grid
    supports_icons = 2
    supports_keyboard_shortcuts = True
    supports_keyboard_boundary_shortcuts = False
    supports_widgets = False
    column_proportion_tolerance = 30

    @property
    def has_focus(self):
        return self.impl.has_focus

    @property
    def font_target(self):
        return self.impl.list_view

    @property
    def row_count(self):
        return len(self.impl._row_cache)

    @property
    def column_count(self):
        return len(self.impl._column_widths)

    def assert_cell_content(self, row, col, value=None, icon=None, widget=None):
        if widget:
            pytest.skip("WinUI doesn't support widgets in Tables")
        cell = self.impl._row_cache[row][col]
        assert cell.text == value
        assert cell.icon == icon

    @property
    def max_scroll_position(self):
        return max(0, self.row_count * ROW_HEIGHT - self.height)

    @property
    def scroll_position(self):
        return min(self.impl._scroll_row * ROW_HEIGHT, self.max_scroll_position)

    async def wait_for_scroll_completion(self):
        pass

    @property
    def header_visible(self):
        return self.widget.show_headings

    @property
    def header_titles(self):
        return self.widget.headings or []

    def column_width(self, index):
        return round(self.impl._column_widths[index])

    async def resize_column(self, index, width):
        self.impl.resize_column(index, width)

    async def select_row(self, row, add=False):
        self.impl.select_row(row, add=add)

    async def activate_row(self, row):
        self.impl.activate_row(row)

    async def select_first_row_keyboard(self):
        self.impl.select_first_row()

    async def type_character(self, char, *, shift=False, ctrl=False, alt=False):
        if char in {"a", "<down>"}:
            self.impl.select_next_row(add=shift)
        elif char == "<up>":
            self.impl.select_previous_row(add=shift)

    async def select_all(self):
        if self.impl.interface.multiple_select:
            self.impl._selection = list(range(len(self.impl._data)))
            self.impl.interface.on_select()

    async def activate_header(self):
        pass
