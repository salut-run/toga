import winreg
from functools import cache
from pathlib import Path

from fontTools.ttLib import TTFont, TTLibError
from win32more.Microsoft.UI.Xaml.Media import FontFamily
from win32more.Windows.UI.Text import FontStyle as NativeFontStyle, FontWeights

from toga.fonts import (
    _IMPL_CACHE,
    _REGISTERED_FONT_CACHE,
    BOLD,
    CURSIVE,
    FANTASY,
    ITALIC,
    MESSAGE,
    MONOSPACE,
    OBLIQUE,
    SANS_SERIF,
    SERIF,
    SYSTEM,
    SYSTEM_DEFAULT_FONT_SIZE,
    UnknownFontError,
)

DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 14
REGISTERED_FONT_SOURCES = {}


@cache
def system_font_families():
    families = set()
    for root in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            key = winreg.OpenKey(
                root,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts",
            )
        except FileNotFoundError:
            continue

        with key:
            index = 0
            while True:
                try:
                    name, _value, _type = winreg.EnumValue(key, index)
                except OSError:
                    break

                families.add(name.split(" (", maxsplit=1)[0])
                index += 1

    return families


def is_system_font(family):
    return any(
        font == family or font.startswith(f"{family} ")
        for font in system_font_families()
    )


def registered_font_family(font_path):
    try:
        font = TTFont(font_path)
    except TTLibError as exc:
        raise ValueError(f"Unable to load font file {font_path}") from exc

    try:
        for name_id in (16, 1):
            for name in font["name"].names:
                if name.nameID == name_id:
                    try:
                        family = name.toUnicode()
                    except UnicodeDecodeError:
                        continue

                    if family:
                        return family
    except KeyError as exc:
        raise ValueError(f"Unable to load font file {font_path}") from exc
    finally:
        font.close()

    raise ValueError(f"Unable to load font file {font_path}")


class Font:
    def __init__(self, interface):
        self.interface = interface

    def load_predefined_system_font(self):
        """Use one of the system font names Toga predefines."""
        try:
            font_family = {
                SYSTEM: DEFAULT_FONT_FAMILY,
                MESSAGE: DEFAULT_FONT_FAMILY,
                SERIF: "Times New Roman",
                SANS_SERIF: DEFAULT_FONT_FAMILY,
                CURSIVE: "Comic Sans MS",
                FANTASY: "Impact",
                MONOSPACE: "Consolas",
            }[self.interface.family]
        except KeyError as exc:
            msg = f"{self.interface} not a predefined system font"
            raise UnknownFontError(msg) from exc

        self._assign_native(font_family)

    def load_user_registered_font(self):
        font_key = self.interface._registered_font_key(
            self.interface.family,
            weight=self.interface.weight,
            style=self.interface.style,
            variant=self.interface.variant,
        )
        try:
            font_path = Path(_REGISTERED_FONT_CACHE[font_key])
        except KeyError as exc:
            msg = f"{self.interface} not a user-registered font"
            raise UnknownFontError(msg) from exc

        if not font_path.exists():
            raise ValueError(f"Font file {font_path} could not be found")

        font_source = (
            f"{font_path.resolve().as_uri()}#{registered_font_family(font_path)}"
        )
        REGISTERED_FONT_SOURCES[font_key] = font_source
        self._assign_native(font_source)

    def load_arbitrary_system_font(self):
        if not is_system_font(self.interface.family):
            msg = f"{self.interface} not found installed on system"
            raise UnknownFontError(msg)

        self._assign_native(self.interface.family)

    def _assign_native(self, font_family):
        self.native_family = FontFamily(font_family)
        self.native_size = (
            DEFAULT_FONT_SIZE
            if self.interface.size == SYSTEM_DEFAULT_FONT_SIZE
            else self.interface.size
        )
        self.native_weight = (
            FontWeights.Bold if self.interface.weight == BOLD else FontWeights.Normal
        )
        self.native_style = {
            ITALIC: NativeFontStyle.Italic,
            OBLIQUE: NativeFontStyle.Oblique,
        }.get(self.interface.style, NativeFontStyle.Normal)
        _IMPL_CACHE[self.interface] = self
