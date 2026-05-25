from functools import cache

from win32more.Microsoft.UI.Xaml.Media import SolidColorBrush
from win32more.Windows.UI import Color as NativeColor

from toga import rgba as TogaColor
from toga.constants import TRANSPARENT


@cache
def native_color(toga_color):
    if not toga_color:
        return None

    if toga_color == TRANSPARENT:
        toga_color = TogaColor(0, 0, 0, 0)

    color = NativeColor()
    color.R = toga_color.rgb.r
    color.G = toga_color.rgb.g
    color.B = toga_color.rgb.b
    color.A = round(toga_color.rgb.a * 255)

    return color


@cache
def native_brush(toga_color):
    if not toga_color:
        return None

    color = native_color(toga_color)

    return SolidColorBrush(color)
