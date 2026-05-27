from win32more.Microsoft.UI.Xaml.Media import FontFamily
from win32more.Windows.UI.Text import FontStyle as NativeFontStyle, FontWeights

from toga.fonts import (
    _IMPL_CACHE,
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
        msg = f"{self.interface} not a user-registered font"
        raise UnknownFontError(msg)

    def load_arbitrary_system_font(self):
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
