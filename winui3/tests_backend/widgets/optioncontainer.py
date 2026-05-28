from win32more.Microsoft.UI.Xaml.Controls import ImageIconSource, TabView
from win32more.Microsoft.UI.Xaml.Media.Imaging import BitmapImage

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
        actual = self.impl.get_option_icon(index)
        native_icon = self.impl.tabs[index].IconSource
        if expected is None:
            assert actual is None
            assert native_icon is None
        else:
            assert actual is not None
            assert actual.path.name == expected
            image_source = native_icon.as_(ImageIconSource).ImageSource
            assert image_source is not None
            assert image_source.as_(BitmapImage).UriSource.RawUri.endswith(
                f"{expected}-windows.png"
            )
