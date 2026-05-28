from toga.sources import ListListener

from ._multicolumn import MulticolumnListView
from .base import SourceListenerCompatibility


class Table(SourceListenerCompatibility, MulticolumnListView, ListListener):
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

    def _columns_changed(self):
        self.update_data()

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

    def select_next_row_wrapping(self):
        if not len(self._data):
            return

        if self.interface.multiple_select:
            current = max(self._selection, default=-1)
        else:
            current = -1 if self._selection is None else self._selection
        self.select_row((current + 1) % len(self._data))

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

    def select_last_row(self):
        if len(self._data):
            self.select_row(len(self._data) - 1)

    def activate_row(self, row):
        self.select_row(row)
        self.interface.on_activate(row=self._data[row])
