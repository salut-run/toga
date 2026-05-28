from win32more.Microsoft.UI.Xaml.Controls import TabView

from .base import SimpleProbe


class OptionContainerProbe(SimpleProbe):
    native_class = TabView
    max_tabs = None
    disabled_tab_selectable = False

    def assert_supports_content_based_rehint(self):
        pass

    def select_tab(self, index):
        if self.tab_enabled(index):
            self.native.SelectedIndex = index

    def tab_enabled(self, index):
        return self.impl.tabs[index].IsEnabled

    async def wait_for_tab(self, message):
        await self.redraw(message)

    def assert_tab_icon(self, index, expected):
        assert self.widget.content[index].icon is None
