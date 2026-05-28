import asyncio

from win32more.Microsoft.UI.Xaml.Controls import ListView

from .base import SimpleProbe

ROW_HEIGHT = 64


class DetailedListProbe(SimpleProbe):
    native_class = ListView
    supports_actions = True
    supports_refresh = True

    @property
    def row_count(self):
        return len(self.impl._row_cache)

    def assert_cell_content(self, row, title, subtitle, icon=None):
        title_value, subtitle_value, icon_value = self.impl._row_cache[row]

        assert title_value == title
        assert subtitle_value == subtitle
        assert icon_value == icon

    @property
    def max_scroll_position(self):
        return max(0, self.row_count * ROW_HEIGHT - self.height)

    @property
    def scroll_position(self):
        return min(self.impl._scroll_row * ROW_HEIGHT, self.max_scroll_position)

    def scroll_to_top(self):
        self.impl.scroll_to_row(0)

    async def wait_for_scroll_completion(self):
        pass

    async def select_row(self, row, add=False):
        self.impl.select_row(row)

    async def deselect_all(self):
        self.impl.deselect_all()

    def refresh_available(self):
        return self.impl.refresh_enabled and self.scroll_position <= 0

    async def non_refresh_action(self):
        pass

    async def refresh_action(self, active=True):
        if active:
            assert self.refresh_available()
        self.impl.refresh_action(active=active)
        await asyncio.sleep(0)

    async def perform_primary_action(self, row, active=True):
        self.impl.primary_action(row, active=active)
        await asyncio.sleep(0)

    async def perform_secondary_action(self, row, active=True):
        self.impl.secondary_action(row, active=active)
        await asyncio.sleep(0)
