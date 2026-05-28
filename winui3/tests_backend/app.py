from ctypes import sizeof
from pathlib import Path

import pytest
from win32more import ComError
from win32more.Microsoft.UI.Xaml.Controls import (
    MenuBarItem,
    MenuFlyoutItem,
    MenuFlyoutSeparator,
    MenuFlyoutSubItem,
)
from win32more.Windows.System import VirtualKeyModifiers
from win32more.Windows.Win32.UI.Input.KeyboardAndMouse import (
    INPUT,
    INPUT_KEYBOARD,
    KEYBDINPUT,
    KEYEVENTF_KEYUP,
    VK_CONTROL,
    VK_LWIN,
    VK_MENU,
    VK_SHIFT,
    SendInput,
)

from toga.command import Separator
from toga_winui3.keys import toga_to_winui_key, winui_to_toga_key

from .dialogs import DialogsMixin
from .probe import BaseProbe


class AppProbe(BaseProbe, DialogsMixin):
    formal_name = "Toga Testbed (WinUI 3)"
    supports_key = True
    supports_key_mod3 = True
    supports_current_window_assignment = True
    supports_dark_mode = True
    edit_menu_noop_enabled = False
    supports_psutil = True

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.main_window = app.main_window
        assert self.app._impl.native_instance is not None

    @property
    def config_path(self):
        return Path.home() / "AppData/Local/Tiberius Yak/Toga Testbed/Config"

    @property
    def data_path(self):
        return Path.home() / "AppData/Local/Tiberius Yak/Toga Testbed/Data"

    @property
    def cache_path(self):
        return Path.home() / "AppData/Local/Tiberius Yak/Toga Testbed/Cache"

    @property
    def logs_path(self):
        return Path.home() / "AppData/Local/Tiberius Yak/Toga Testbed/Logs"

    @property
    def is_cursor_visible(self):
        return self.app._impl._cursor_visible

    def unhide(self):
        pytest.xfail("WinUI 3 doesn't have an app level unhide.")

    def assert_app_icon(self, icon):
        expected_path = self.app.icon._impl.path
        if icon is not None:
            assert expected_path.stem == Path(icon).name

        for window in self.app.windows:
            assert window._impl.icon._impl.path == expected_path

    def activate_menu_hide(self):
        pytest.xfail("WinUI 3 doesn't present an app level hide option in menu.")

    def activate_menu_exit(self):
        self._activate_menu_item(["File", "Exit"])

    def activate_menu_about(self):
        self._activate_menu_item(["Help", f"About {self.formal_name}"])

    async def close_about_dialog(self):
        self.app._impl._about_dialog.Hide()

    def activate_menu_visit_homepage(self):
        self._activate_menu_item(["Help", "Visit homepage"])

    def assert_dialog_in_focus(self, dialog):
        assert dialog._impl is not None

    def assert_menu_item(self, path, *, enabled=True):
        item = self._menu_item(path)
        native = (
            self._as(item, MenuFlyoutItem)
            or self._as(item, MenuFlyoutSubItem)
            or self._as(item, MenuBarItem)
        )
        assert native.IsEnabled == enabled

        if menu_item := self._as(item, MenuFlyoutItem):
            try:
                shortcut = {
                    ("Other", "Full command"): "Ctrl+1",
                    ("Other", "Submenu1", "Disabled"): "",
                    ("Commands", "No Tooltip"): "Ctrl+Down",
                    ("Commands", "Sectioned"): "Ctrl+Space",
                }[tuple(path)]
            except KeyError:
                pass
            else:
                assert menu_item.KeyboardAcceleratorTextOverride == shortcut

    def assert_menu_order(self, path, expected):
        actual = [self._menu_item_label(item) for item in self._menu_items(path)]
        assert actual == expected

    def assert_system_menus(self):
        self.assert_menu_item(["File", "New Example Document"], enabled=True)
        self.assert_menu_item(["File", "New Read-only Document"], enabled=True)
        self.assert_menu_item(["File", "Open..."], enabled=True)
        self.assert_menu_item(["File", "Save"], enabled=True)
        self.assert_menu_item(["File", "Save As..."], enabled=True)
        self.assert_menu_item(["File", "Save All"], enabled=True)
        self.assert_menu_item(["File", "Preferences"], enabled=False)
        self.assert_menu_item(["File", "Exit"], enabled=True)

        self.assert_menu_item(["Help", "Visit homepage"], enabled=True)
        self.assert_menu_item(["Help", "About Toga Testbed (WinUI 3)"], enabled=True)

    def _as(self, item, native_cls):
        try:
            return item.as_(native_cls)
        except (ComError, OSError):
            return None

    def _native_menu_items(self, native):
        native = (
            native
            if hasattr(native, "Items")
            else self._as(native, MenuBarItem) or self._as(native, MenuFlyoutSubItem)
        )
        return [native.Items.GetAt(index) for index in range(len(native.Items))]

    def _menu_item_label(self, item):
        if self._as(item, MenuFlyoutSeparator) is not None:
            return "---"
        if native := self._as(item, MenuBarItem):
            return native.Title
        if native := self._as(item, MenuFlyoutSubItem):
            return native.Text
        if native := self._as(item, MenuFlyoutItem):
            return native.Text

        raise AssertionError(f"Unknown WinUI menu item type: {item!r}")

    def _menu_item(self, path):
        item = self.main_window._impl.menu_native
        for index, label in enumerate(path):
            children = self._native_menu_items(item)
            child_labels = [self._menu_item_label(child) for child in children]
            try:
                item = children[child_labels.index(label)]
            except ValueError:
                raise AssertionError(
                    f"no item named {path[: index + 1]}; options are {child_labels}"
                ) from None

        return item

    def _menu_items(self, path):
        return self._native_menu_items(self._menu_item(path))

    def _activate_menu_item(self, path):
        item = self._menu_item(path).as_(MenuFlyoutItem)
        for cmd in self.app.commands:
            if isinstance(cmd, Separator):
                continue
            if item in cmd._impl.native:
                cmd.action()
                return

        raise AssertionError(f"no command associated with {' > '.join(path)}")

    def _key_value(self, value):
        return value.value if hasattr(value, "value") else value

    def _keyboard_input(self, key, flags=0):
        native_input = INPUT()
        native_input.type = INPUT_KEYBOARD
        native_input.ki = KEYBDINPUT(self._key_value(key), 0, flags, 0, 0)
        return native_input

    def _send_keyboard_inputs(self, inputs):
        INPUT_ARRAY = INPUT * len(inputs)
        native_inputs = INPUT_ARRAY(*inputs)
        result = SendInput(len(native_inputs), native_inputs, sizeof(INPUT))
        if result != len(native_inputs):
            raise RuntimeError(
                f"SendInput sent {result} of {len(native_inputs)} keyboard inputs"
            )

    def activate_menu_shortcut(self, path):
        item = self._menu_item(path).as_(MenuFlyoutItem)
        if len(item.KeyboardAccelerators) != 1:
            raise AssertionError(f"expected one keyboard accelerator for {path!r}")

        accelerator = item.KeyboardAccelerators.GetAt(0)
        modifiers = self._key_value(accelerator.Modifiers)
        modifier_keys = []
        for modifier, key in [
            (VirtualKeyModifiers.Control, VK_CONTROL),
            (VirtualKeyModifiers.Menu, VK_MENU),
            (VirtualKeyModifiers.Shift, VK_SHIFT),
            (VirtualKeyModifiers.Windows, VK_LWIN),
        ]:
            if modifiers & self._key_value(modifier):
                modifier_keys.append(key)

        self.main_window._impl.native.Activate()
        self._send_keyboard_inputs(
            [
                *[self._keyboard_input(key) for key in modifier_keys],
                self._keyboard_input(accelerator.Key),
                self._keyboard_input(accelerator.Key, KEYEVENTF_KEYUP),
                *[
                    self._keyboard_input(key, KEYEVENTF_KEYUP)
                    for key in reversed(modifier_keys)
                ],
            ]
        )

    def _activate_native_menu_item(self, path):
        item = self._menu_item(path).as_(MenuFlyoutItem)
        for native_item, action in self.main_window._impl.window_menu_actions:
            if item == native_item:
                action()
                return

        raise AssertionError(f"no native action associated with {' > '.join(path)}")

    def activate_menu_close_window(self):
        self._activate_native_menu_item(["File", "Close"])

    def activate_menu_close_all_windows(self):
        self._activate_native_menu_item(["File", "Close All"])

    def activate_menu_minimize(self):
        self._activate_native_menu_item(["Window", "Minimize"])

    def keystroke(self, combination):
        key, modifiers = toga_to_winui_key(combination)
        return winui_to_toga_key(key, modifiers)

    async def restore_standard_app(self):
        await self.redraw("Restore to standard app")

    async def open_initial_document(self, monkeypatch, document_path):
        self.app._impl.open_initial_documents([document_path])
        await self.redraw("Initial document has been triggered")

    def open_document_by_drag(self, document_path):
        self.main_window._impl.open_dropped_files([document_path])

    def has_status_icon(self, status_icon):
        return status_icon._impl.has_native_icon()

    def status_menu_items(self, status_icon):
        if not hasattr(status_icon._impl, "menu"):
            return None

        return [
            {
                f"About {self.formal_name}": "**ABOUT**",
                "Exit": "**EXIT**",
            }.get(item["text"], item["text"])
            for item in status_icon._impl.menu
        ]

    def activate_status_icon_button(self, item_id):
        self.app.status_icons[item_id]._impl.winui_click()

    def activate_status_menu_item(self, item_id, title):
        for item in self.app.status_icons[item_id]._impl.menu:
            if item["text"] == title:
                item["command"].action()
                return

        raise AssertionError(f"No status menu item named {title!r}")
