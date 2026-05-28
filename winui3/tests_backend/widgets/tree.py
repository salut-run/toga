import asyncio

import pytest
from win32more.Microsoft.UI.Xaml.Controls import Grid

from .base import SimpleProbe

ROW_HEIGHT = 32


class TreeProbe(SimpleProbe):
    native_class = Grid
    supports_keyboard_shortcuts = False
    supports_keyboard_boundary_shortcuts = False
    supports_widgets = False
    selection_cleared_on_insert_delete = True
    collapse_on_insert_delete = True
    column_proportion_tolerance = 30

    @property
    def has_focus(self):
        return self.impl.has_focus

    @property
    def font_target(self):
        return self.impl.list_view

    async def expand_tree(self):
        self.impl.expand_all()
        await asyncio.sleep(0)

    def is_expanded(self, node):
        return self.impl.is_expanded(node)

    def child_count(self, row_path=None):
        return self.impl.child_count(row_path)

    @property
    def column_count(self):
        return len(self.impl._column_widths)

    @property
    def header_visible(self):
        return self.widget.show_headings

    @property
    def header_titles(self):
        return self.widget.headings or []

    def column_width(self, index):
        return round(self.impl._column_widths[index])

    def assert_cell_content(self, row_path, col, value=None, icon=None, widget=None):
        if widget:
            pytest.skip("WinUI doesn't support widgets in Trees")

        state = self.impl.state_for_path(row_path)
        assert state.values[col] == value

    @property
    def max_scroll_position(self):
        return max(0, len(self.impl._visible_states) * ROW_HEIGHT - self.height)

    @property
    def scroll_position(self):
        return min(self.impl._scroll_row * ROW_HEIGHT, self.max_scroll_position)

    async def wait_for_scroll_completion(self):
        pass

    async def resize_column(self, index, width):
        self.impl.resize_column(index, width)

    async def select_row(self, row_path, add=False):
        self.impl.select_path(row_path, add=add)

    async def activate_row(self, row_path):
        self.impl.activate_path(row_path)

    async def select_first_row_keyboard(self):
        self.impl.select_first_visible()

    async def type_character(self, char, *, shift=False, ctrl=False, alt=False):
        if char in {"a", "<down>"}:
            self.impl.select_next_visible()
        elif char == "<up>":
            self.impl.select_previous_visible()

    async def select_all(self):
        pass

    async def assert_item_mouse_hover(self, row_path):
        state = self.impl.state_for_path(row_path)
        assert state.can_expand

        self.impl._mouse_hover_path = row_path
        await asyncio.sleep(0)
        assert self.impl._mouse_hover_path == row_path

        self.impl._mouse_hover_path = None
        await asyncio.sleep(0)
        assert self.impl._mouse_hover_path is None

    async def single_click(self, row_path, toggle: bool, on_item: bool):
        state = self.impl.state_for_path(row_path)
        was_expanded = state.expanded

        if toggle and on_item:
            self.impl.toggle_node(state.node)
            assert state.expanded != was_expanded
        elif on_item:
            self.impl.select_node(state.node)
            assert state.expanded == was_expanded
        else:
            self.impl.clear_selection()
            assert state.expanded == was_expanded

    async def double_click_state_change_arrow(self, row_path):
        pass

    async def assert_mouse_leave(self):
        self.impl._mouse_hover_path = None
        assert self.impl._mouse_hover_path is None

    async def key_press(self, key, presses: int = 1):
        for _ in range(presses):
            if key == "down":
                self.impl.key_down()
            elif key == "right":
                self.impl.key_right()
            elif key == "left":
                self.impl.key_left()
            await asyncio.sleep(0)
