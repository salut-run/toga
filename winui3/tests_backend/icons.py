from pathlib import Path

import pytest

import toga
import toga_winui3
from toga_winui3.icons import Icon as WinUIIcon

from .probe import BaseProbe


class IconProbe(BaseProbe):
    alternate_resource = "resources/icons/blue"

    def __init__(self, app, icon):
        super().__init__()
        self.app = app
        self.icon = icon
        assert isinstance(self.icon._impl, WinUIIcon)

    def assert_icon_content(self, path):
        if path == "resources/icons/green":
            assert (
                self.icon._impl.path == self.app.paths.app / "resources/icons/green.png"
            )
        elif path == "resources/icons/blue":
            assert (
                self.icon._impl.path == self.app.paths.app / "resources/icons/blue.png"
            )
        else:
            pytest.fail("Unknown icon resource")

    def assert_default_icon_content(self):
        assert (
            self.icon._impl.path
            == Path(toga_winui3.__file__).parent / "resources/toga.png"
        )

    def assert_platform_icon_content(self):
        assert self.icon._impl.path == self.app.paths.app / "resources/logo-windows.ico"

    def assert_app_icon_content(self):
        assert self.icon._impl == toga.Icon.DEFAULT_ICON._impl
