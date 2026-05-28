from toga.sources import TreeListener

from ._multicolumn import MulticolumnListView
from .base import SourceListenerCompatibility


class TreeStateNode:
    def __init__(self, node, parent=None, depth=0):
        self.node = node
        self.parent = parent
        self.depth = depth
        self.expanded = False
        self.values = []

        if node.can_have_children():
            self.children = [
                TreeStateNode(child, parent=self, depth=depth + 1) for child in node
            ]
        else:
            self.children = None

    def __len__(self):
        return len(self.children or [])

    def __getitem__(self, path):
        if path is None or len(path) == 0:
            return self

        if self.children is None:
            raise IndexError(path)

        child = self.children[path[0]]
        if len(path) == 1:
            return child
        return child[path[1:]]

    @property
    def can_expand(self):
        return self.children is not None

    def all_states(self):
        yield self
        for child in self.children or []:
            yield from child.all_states()

    def visible_states(self):
        yield self
        if self.expanded:
            for child in self.children or []:
                yield from child.visible_states()

    def set_expanded_recursive(self, expanded):
        if self.can_expand:
            self.expanded = expanded
            for child in self.children:
                child.set_expanded_recursive(expanded)


class Tree(SourceListenerCompatibility, MulticolumnListView, TreeListener):
    SOURCE_SUPPORTS_PARENT = True

    def _initialize_data_state(self):
        super()._initialize_data_state()
        self._focused_node = None
        self._state_roots = []
        self._state_by_node = {}
        self._visible_states = []
        self._mouse_hover_path = None

    def change_source(self, source):
        self._clear_selection()
        self.update_data()

    def update_data(self):
        self._state_roots = [
            TreeStateNode(self._data[index]) for index in range(len(self._data))
        ]
        self._state_by_node = {}
        for state in self._all_states():
            self._state_by_node[state.node] = state
            state.values = self._row_values(state.node)

        self._refresh_visible_rows()
        self._coerce_selection()
        self.interface.refresh()

    def source_insert(self, *, index, item, parent=None):
        self._clear_selection()
        self.update_data()

    def source_change(self, *, item):
        try:
            state = self._state_by_node[item]
        except KeyError:
            self.update_data()
        else:
            state.values = self._row_values(item)
            self._refresh_visible_rows()
            self._coerce_selection()
            self.interface.refresh()

    def source_remove(self, *, index, item, parent=None):
        self._clear_selection()
        self.update_data()

    def source_clear(self):
        self._clear_selection()
        self.update_data()

    def _columns_changed(self):
        for state in self._all_states():
            state.values = self._row_values(state.node)
        self._refresh_visible_rows()

    def _clear_selection(self):
        if self.interface.multiple_select:
            self._selection = []
        else:
            self._selection = None
        self._focused_node = None

    @property
    def _row_count(self):
        return len(self._visible_states)

    def _native_rows(self):
        return self._visible_states

    def _values_for_native_row(self, state):
        return state.values

    def _display_parts(self, state, index, value):
        text = "" if value is None else str(value)
        if index != 0:
            return "", text

        indentation = " " * int(state.depth * 2)
        if state.can_expand:
            arrow = "v " if state.expanded else "> "
        else:
            arrow = "  "
        return f"{indentation}{arrow}", text

    def _refresh_visible_rows(self):
        self._visible_states = []
        for state in self._state_roots:
            self._visible_states.extend(state.visible_states())
        self._sync_native_rows()

    def _coerce_selection(self):
        if self.interface.multiple_select:
            self._selection = [
                node for node in self._selection if node in self._state_by_node
            ]
            self._selection.sort(key=self._display_sort_key)
        elif self._selection not in self._state_by_node:
            self._selection = None

        if self._focused_node not in self._state_by_node:
            self._focused_node = None

    def _display_sort_key(self, node):
        try:
            return self._visible_states.index(self._state_by_node[node])
        except ValueError:
            return len(self._visible_states)

    def _all_states(self):
        for state in self._state_roots:
            yield from state.all_states()

    def state_for_node(self, node):
        return self._state_by_node.get(node)

    def state_for_path(self, path=None):
        if path is None or len(path) == 0:
            return None

        state = self._state_roots[path[0]]
        if len(path) == 1:
            return state
        return state[path[1:]]

    def child_count(self, path=None):
        if path is None:
            return len(self._state_roots)
        return len(self.state_for_path(path))

    def is_expanded(self, node):
        state = self.state_for_node(node)
        return bool(state and state.expanded)

    def expand_all(self):
        for state in self._state_roots:
            state.set_expanded_recursive(True)
        self._refresh_visible_rows()

    def expand_node(self, node):
        state = self.state_for_node(node)
        if state is not None:
            state.set_expanded_recursive(True)
            self._refresh_visible_rows()

    def collapse_all(self):
        for state in self._state_roots:
            state.set_expanded_recursive(False)
        self._refresh_visible_rows()

    def collapse_node(self, node):
        state = self.state_for_node(node)
        if state is not None and state.can_expand:
            state.set_expanded_recursive(False)
            self._refresh_visible_rows()

    def toggle_node(self, node):
        state = self.state_for_node(node)
        if state is not None and state.can_expand:
            state.expanded = not state.expanded
            self._refresh_visible_rows()

    def select_node(self, node, add=False):
        if node not in self._state_by_node:
            return

        if self.interface.multiple_select:
            if add:
                if node in self._selection:
                    self._selection.remove(node)
                else:
                    self._selection.append(node)
                    self._selection.sort(key=self._display_sort_key)
            else:
                self._selection = [node]
        else:
            self._selection = node

        self._focused_node = node
        self.interface.on_select()

    def clear_selection(self):
        self._clear_selection()
        self.interface.on_select()

    def select_path(self, path, add=False):
        self.select_node(self.state_for_path(path).node, add=add)

    def activate_path(self, path):
        state = self.state_for_path(path)
        self.select_node(state.node)
        self.interface.on_activate(node=state.node)

    def select_next_visible(self):
        if not self._visible_states:
            return

        current = self._focused_visible_index()
        self.select_node(
            self._visible_states[min(current + 1, len(self._visible_states) - 1)].node
        )

    def select_previous_visible(self):
        if not self._visible_states:
            return

        current = self._focused_visible_index()
        self.select_node(self._visible_states[max(current - 1, 0)].node)

    def select_first_visible(self):
        if self._visible_states:
            self.select_node(self._visible_states[0].node)

    def _focused_visible_index(self):
        node = self._focused_node
        if node is None:
            if self.interface.multiple_select:
                node = self._selection[-1] if self._selection else None
            else:
                node = self._selection

        if node in self._state_by_node:
            try:
                return self._visible_states.index(self._state_by_node[node])
            except ValueError:
                pass
        return 0

    def key_down(self):
        self.select_next_visible()

    def key_right(self):
        node = self._focused_node
        if node is not None:
            state = self.state_for_node(node)
            if state is not None and state.can_expand and not state.expanded:
                state.expanded = True
                self._refresh_visible_rows()

    def key_left(self):
        node = self._focused_node
        if node is not None:
            state = self.state_for_node(node)
            if state is not None and state.can_expand and state.expanded:
                state.expanded = False
                self._refresh_visible_rows()
