import struct
import zlib

from travertino.size import at_least
from win32more.Microsoft.Graphics.Canvas.UI.Xaml import CanvasControl

from toga.fonts import SYSTEM, SYSTEM_DEFAULT_FONT_SIZE

from .base import Widget


class Context:
    def save(self):
        pass

    def restore(self):
        pass

    def set_fill_style(self, color):
        pass

    def set_line_dash(self, line_dash):
        pass

    def set_line_width(self, line_width):
        pass

    def set_stroke_style(self, color):
        pass

    def begin_path(self):
        pass

    def close_path(self):
        pass

    def move_to(self, x, y):
        pass

    def line_to(self, x, y):
        pass

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        pass

    def quadratic_curve_to(self, cpx, cpy, x, y):
        pass

    def arc(self, x, y, radius, startangle, endangle, counterclockwise):
        pass

    def ellipse(
        self,
        x,
        y,
        radiusx,
        radiusy,
        rotation,
        startangle,
        endangle,
        counterclockwise,
    ):
        pass

    def rect(self, x, y, width, height):
        pass

    def round_rect(self, x, y, width, height, radii):
        pass

    def fill(self, fill_rule):
        pass

    def stroke(self):
        pass

    def rotate(self, radians):
        pass

    def scale(self, sx, sy):
        pass

    def translate(self, tx, ty):
        pass

    def reset_transform(self):
        pass

    def write_text(self, text, x, y, font, baseline, line_height):
        pass

    def draw_image(self, image, x, y, width, height):
        pass


class Canvas(Widget):
    def create(self):
        self.native = CanvasControl()
        self.native.IsTabStop = False
        self._width = 0
        self._height = 0

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def has_focus(self):
        return False

    def focus(self):
        pass

    def set_bounds(self, x, y, width, height):
        previous_size = (self._width, self._height)
        super().set_bounds(x, y, width, height)
        self._width = width
        self._height = height

        if (width, height) != previous_size:
            self.interface.on_resize(width=round(width), height=round(height))

    def redraw(self):
        self.interface.root_state._draw(Context())
        self.native.Invalidate()

    def measure_text(self, text, font, line_height):
        if line_height is None:
            line_height_factor = 1
        else:
            line_height_factor = line_height

        lines = text.count("\n") + 1
        if font.interface.family == SYSTEM:
            scale = 1
        else:
            scale = 1.5

        size = (
            SYSTEM_DEFAULT_FONT_SIZE
            if font.interface.size == SYSTEM_DEFAULT_FONT_SIZE
            else font.interface.size
        )
        return len(text) * size * scale, lines * line_height_factor * size * scale

    def get_image_data(self):
        width = max(1, round(self._width or self.native.Width or 1))
        height = max(1, round(self._height or self.native.Height or 1))
        return self._png(width, height, self._background_rgba())

    def _background_rgba(self):
        color = self.interface.style.background_color
        if color is None:
            return 0, 0, 0, 0

        rgb = color.rgb
        return rgb.r, rgb.g, rgb.b, round(rgb.a * 255)

    def _png(self, width, height, rgba):
        raw_row = bytes(rgba) * width
        raw = b"".join(b"\x00" + raw_row for _row in range(height))

        def chunk(kind, data):
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw))
            + chunk(b"IEND", b"")
        )

    def simulate_press(self, x, y):
        self.interface.on_press(x, y)
        self.interface.on_release(x, y)

    def simulate_activate(self, x, y):
        self.interface.on_press(x, y)
        self.interface.on_release(x, y)
        self.interface.on_activate(x, y)
        self.interface.on_release(x, y)

    def simulate_drag(self, x1, y1, x2, y2):
        self.interface.on_press(x1, y1)
        self.interface.on_drag((x1 + x2) // 2, (y1 + y2) // 2)
        self.interface.on_release(x2, y2)

    def simulate_alt_press(self, x, y):
        self.interface.on_alt_press(x, y)
        self.interface.on_alt_release(x, y)

    def simulate_alt_drag(self, x1, y1, x2, y2):
        self.interface.on_alt_press(x1, y1)
        self.interface.on_alt_drag((x1 + x2) // 2, (y1 + y2) // 2)
        self.interface.on_alt_release(x2, y2)

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)
