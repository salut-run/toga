from win32more.Windows.UI.Text import FontStyle as NativeFontStyle

from toga.fonts import (
    _REGISTERED_FONT_CACHE,
    BOLD,
    CURSIVE,
    FANTASY,
    ITALIC,
    MESSAGE,
    MONOSPACE,
    NORMAL,
    OBLIQUE,
    SANS_SERIF,
    SERIF,
    SMALL_CAPS,
    SYSTEM,
    SYSTEM_DEFAULT_FONT_SIZE,
    Font,
)
from toga_winui3.fonts import (
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    REGISTERED_FONT_SOURCES,
)


class FontMixin:
    supports_custom_fonts = True
    supports_custom_variable_fonts = False

    def preinstalled_font(self):
        return "Times New Roman"

    @property
    def font_target(self):
        return self.native

    def assert_font_options(self, weight=NORMAL, style=NORMAL, variant=NORMAL):
        assert weight == (BOLD if self.font_target.FontWeight.Weight >= 700 else NORMAL)

        if style == OBLIQUE:
            assert self.font_target.FontStyle == NativeFontStyle.Oblique
        else:
            assert style == (
                ITALIC
                if self.font_target.FontStyle == NativeFontStyle.Italic
                else NORMAL
            )

        if variant == SMALL_CAPS:
            return
        else:
            assert variant == NORMAL

    def assert_font_size(self, expected):
        if expected == SYSTEM_DEFAULT_FONT_SIZE:
            expected = DEFAULT_FONT_SIZE
        assert round(self.font_target.FontSize) == expected

    def assert_font_family(self, expected):
        font_key = Font._registered_font_key(
            expected,
            self.widget.style.font_weight,
            self.widget.style.font_style,
            self.widget.style.font_variant,
        )
        if font_key in _REGISTERED_FONT_CACHE:
            assert (
                self.font_target.FontFamily.Source == REGISTERED_FONT_SOURCES[font_key]
            )
            return

        assert self.font_target.FontFamily.Source == {
            CURSIVE: "Comic Sans MS",
            FANTASY: "Impact",
            MESSAGE: DEFAULT_FONT_FAMILY,
            MONOSPACE: "Consolas",
            SANS_SERIF: DEFAULT_FONT_FAMILY,
            SERIF: "Times New Roman",
            SYSTEM: DEFAULT_FONT_FAMILY,
        }.get(expected, expected)
