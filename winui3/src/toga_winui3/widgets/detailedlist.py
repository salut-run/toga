from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import (
    Image as NativeImage,
    ListView,
    ListViewItem,
    ListViewSelectionMode,
    Orientation,
    StackPanel,
    TextBlock,
)
from win32more.Microsoft.UI.Xaml.Media import Stretch

from toga.sources import ListListener

from .base import SourceListenerCompatibility, Widget

ROW_HEIGHT = 64
ICON_SIZE = 32


class DetailedList(SourceListenerCompatibility, Widget, ListListener):
    def create(self):
        self.native = ListView()
        self.native.SelectionMode = ListViewSelectionMode.Single
        self.native.IsTabStop = False

        self._selection = None
        self._scroll_row = 0
        self._row_cache = []
        self.primary_action_enabled = False
        self.secondary_action_enabled = False
        self.refresh_enabled = False

    @property
    def _data(self):
        return self.interface.data

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def has_focus(self):
        return False

    def focus(self):
        pass

    def change_source(self, source):
        self._selection = None
        self.update_data()

    def update_data(self):
        self._row_cache = [self._row_values(row) for row in self._data]
        self._sync_native_rows()
        self._coerce_selection()
        self.interface.refresh()

    def _row_values(self, row):
        title_accessor, subtitle_accessor, icon_accessor = self.interface.accessors
        title = getattr(row, title_accessor, None)
        subtitle = getattr(row, subtitle_accessor, None)
        icon = getattr(row, icon_accessor, None)

        return (
            self._text_value(title),
            self._text_value(subtitle),
            icon,
        )

    def _text_value(self, value):
        return self.interface.missing_value if value is None else str(value)

    def _native_row(self, title, subtitle, icon):
        item = ListViewItem()
        item.MinHeight = ROW_HEIGHT

        row = StackPanel()
        row.Orientation = Orientation.Horizontal
        row.MinHeight = ROW_HEIGHT

        image = NativeImage()
        image.Width = ICON_SIZE
        image.Height = ICON_SIZE
        image.Stretch = Stretch.Uniform
        if icon is not None:
            image.Source = icon._impl.bitmap_image(ICON_SIZE)
        row.Children.Append(image)

        text = StackPanel()
        text.Orientation = Orientation.Vertical

        title_block = TextBlock()
        title_block.Text = title
        text.Children.Append(title_block)

        subtitle_block = TextBlock()
        subtitle_block.Text = subtitle
        subtitle_block.FontSize = 12
        text.Children.Append(subtitle_block)

        row.Children.Append(text)
        item.Content = row
        return item

    def _sync_native_rows(self):
        self.native.Items.Clear()
        for title, subtitle, icon in self._row_cache:
            self.native.Items.Append(self._native_row(title, subtitle, icon))

    def _coerce_selection(self):
        if self._selection is not None and self._selection >= len(self._row_cache):
            self._selection = None

    def source_insert(self, *, index, item):
        self.update_data()

    def source_change(self, *, item):
        try:
            index = self._data.index(item)
        except ValueError:
            self.update_data()
        else:
            self._row_cache[index] = self._row_values(item)
            self._sync_native_rows()
            self.interface.refresh()

    def source_remove(self, *, index, item):
        self.update_data()

    def source_clear(self):
        self._selection = None
        self.update_data()

    def scroll_to_row(self, index):
        self._scroll_row = max(0, min(index, max(len(self._row_cache) - 1, 0)))
        if len(self.native.Items):
            self.native.ScrollIntoView(self.native.Items.GetAt(self._scroll_row))

    def get_selection(self):
        return self._selection

    def select_row(self, row):
        if not self._row_cache:
            return

        self._selection = max(0, min(row, len(self._row_cache) - 1))
        self.interface.on_select()

    def deselect_all(self):
        self._selection = None
        self.interface.on_select()

    def set_primary_action_enabled(self, enabled):
        self.primary_action_enabled = enabled

    def set_secondary_action_enabled(self, enabled):
        self.secondary_action_enabled = enabled

    def set_refresh_enabled(self, enabled):
        self.refresh_enabled = enabled

    def after_on_refresh(self, widget, result):
        pass

    def refresh_action(self, active=True):
        if active and self.refresh_enabled:
            self.interface.on_refresh()

    def primary_action(self, row, active=True):
        if active and self.primary_action_enabled:
            self.interface.on_primary_action(row=self._data[row])

    def secondary_action(self, row, active=True):
        if active and self.secondary_action_enabled:
            self.interface.on_secondary_action(row=self._data[row])

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
