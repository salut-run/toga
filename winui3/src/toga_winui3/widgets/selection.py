from contextlib import contextmanager

from travertino.size import at_least
from win32more.Microsoft.UI.Xaml.Controls import ComboBox, ComboBoxItem, TextBlock

from toga.handlers import WeakrefCallable

from .base import (
    SourceListenerCompatibility,
    Widget,
    native_horizontal_alignment,
)


def int_value(value):
    return int(getattr(value, "value", value))


class Selection(SourceListenerCompatibility, Widget):
    CHROME_WIDTH = 48
    CHROME_HEIGHT = 16
    MIN_HEIGHT = 32

    def create(self):
        self.native = ComboBox()
        self.native.MinWidth = 0
        self.native.SelectionChanged += WeakrefCallable(
            self.native_event_selection_changed
        )
        self._item_titles = []
        self._send_notifications = True

    @contextmanager
    def suspend_notifications(self):
        self._send_notifications = False
        try:
            yield
        finally:
            self._send_notifications = True

    def native_event_selection_changed(self, sender, args):
        if self._send_notifications:
            self.interface.on_change()

    def _item_count(self):
        return int_value(self.native.Items.Size)

    def _create_native_item(self, title):
        item = ComboBoxItem()
        item.MinWidth = 0

        item.Content = "\u200b" if title == "" else title

        if hasattr(self, "_font"):
            self._apply_font(item)
        if hasattr(self, "_text_align"):
            item.HorizontalContentAlignment = native_horizontal_alignment(
                self._text_align
            )

        return item

    def _titles(self):
        return list(self._item_titles)

    def _set_selected_index(self, index, *, notify=True):
        old_index = self.get_selected_index()
        if old_index == index:
            return

        with self.suspend_notifications():
            self.native.SelectedIndex = -1 if index is None else index

        if notify:
            self.interface.on_change()

    def set_font(self, font):
        super().set_font(font)
        for index in range(self._item_count()):
            item = self.native.Items.GetAt(index).as_(ComboBoxItem)
            self._apply_font(item)
        self.interface.refresh()

    def set_text_align(self, value):
        super().set_text_align(value)
        alignment = native_horizontal_alignment(value)
        self.native.HorizontalContentAlignment = alignment
        for index in range(self._item_count()):
            item = self.native.Items.GetAt(index).as_(ComboBoxItem)
            item.HorizontalContentAlignment = alignment

    def source_clear(self):
        selected_index = self.get_selected_index()
        with self.suspend_notifications():
            self.native.Items.Clear()
            self._item_titles = []

        if selected_index is not None:
            self.interface.on_change()

        self.interface.refresh()

    def source_insert(self, *, index, item):
        selected_index = self.get_selected_index()
        title = self.interface._title_for_item(item)
        self._item_titles.insert(index, title)
        self.native.Items.InsertAt(
            index,
            self._create_native_item(title),
        )

        if selected_index is None:
            self._set_selected_index(0)
        elif index <= selected_index:
            self._set_selected_index(selected_index + 1, notify=False)

        self.interface.refresh()

    def source_change(self, *, item):
        index = self.interface._items.index(item)
        selected_index = self.get_selected_index()
        title = self.interface._title_for_item(item)
        self._item_titles[index] = title

        with self.suspend_notifications():
            self.native.Items.SetAt(
                index,
                self._create_native_item(title),
            )

        if selected_index is not None:
            self._set_selected_index(selected_index, notify=False)

        self.interface.refresh()

    def source_remove(self, *, index, item):
        selected_index = self.get_selected_index()

        with self.suspend_notifications():
            self.native.Items.RemoveAt(index)
            del self._item_titles[index]

        item_count = self._item_count()
        if selected_index == index:
            if item_count == 0:
                self.interface.on_change()
            else:
                self._set_selected_index(max(0, index - 1))
        elif selected_index is not None and index < selected_index:
            self._set_selected_index(selected_index - 1, notify=False)

        self.interface.refresh()

    def select_item(self, index, item):
        self._set_selected_index(index)

    def get_selected_index(self):
        index = int_value(self.native.SelectedIndex)
        return None if index == -1 else index

    def _measure_text(self, title):
        native = TextBlock()
        native.Text = "\u200b" if title == "" else title
        if hasattr(self, "_font"):
            self._apply_font(native)

        if self.container:
            children = self.container._staging_panel.Children
            children.Append(native)
            try:
                return self.measure_unconstrained(native)
            finally:
                children.RemoveAt(int_value(children.Size) - 1)

        return self.measure_unconstrained(native)

    def rehint(self):
        text_sizes = [
            self._measure_text(title)
            for title in (self._titles() if self._titles() else [""])
        ]
        self.interface.intrinsic.width = at_least(
            max(size.Width for size in text_sizes) + self.CHROME_WIDTH
        )
        self.interface.intrinsic.height = max(
            self.MIN_HEIGHT,
            max(size.Height for size in text_sizes) + self.CHROME_HEIGHT,
        )
