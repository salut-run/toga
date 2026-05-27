from pathlib import Path

import pytest

from .probe import BaseProbe


class AppProbe(BaseProbe):
    supports_key = False
    supports_key_mod3 = False
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
        pytest.skip("WinUI 3 app icon probing is not implemented yet.")

    def activate_menu_hide(self):
        pytest.xfail("WinUI 3 doesn't present an app level hide option in menu.")

    def activate_menu_exit(self):
        self.app.exit()

    def activate_menu_about(self):
        pytest.skip("WinUI 3 about dialog is not implemented yet.")

    async def close_about_dialog(self):
        pytest.skip("WinUI 3 about dialog is not implemented yet.")

    def activate_menu_visit_homepage(self):
        pytest.skip("WinUI 3 menu probing is not implemented yet.")

    def assert_dialog_in_focus(self, dialog):
        pytest.skip("WinUI 3 dialog probing is not implemented yet.")

    def assert_menu_item(self, path, *, enabled=True):
        pytest.skip("WinUI 3 menu probing is not implemented yet.")

    def assert_menu_order(self, path, expected):
        pytest.skip("WinUI 3 menu probing is not implemented yet.")

    def assert_system_menus(self):
        pytest.skip("WinUI 3 menu probing is not implemented yet.")

    def activate_menu_close_window(self):
        pytest.xfail("WinUI 3 window management menu is not implemented yet.")

    def activate_menu_close_all_windows(self):
        pytest.xfail("WinUI 3 window management menu is not implemented yet.")

    def activate_menu_minimize(self):
        pytest.xfail("WinUI 3 window management menu is not implemented yet.")

    def keystroke(self, combination):
        pytest.skip("WinUI 3 keyboard probing is not implemented yet.")

    async def restore_standard_app(self):
        await self.redraw("Restore to standard app")

    async def open_initial_document(self, monkeypatch, document_path):
        pytest.xfail("WinUI 3 doesn't require initial document support.")

    def open_document_by_drag(self, document_path):
        pytest.xfail("WinUI 3 doesn't support opening documents by drag yet.")

    def has_status_icon(self, status_icon):
        return False

    def status_menu_items(self, status_icon):
        return None

    def activate_status_icon_button(self, item_id):
        pytest.skip("WinUI 3 status icons are not implemented yet.")

    def activate_status_menu_item(self, item_id, title):
        pytest.skip("WinUI 3 status icons are not implemented yet.")
