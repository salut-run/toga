import logging
import math
from contextlib import contextmanager
from threading import Event

from travertino.size import at_least
from win32more.Microsoft.Graphics.Canvas import CanvasBitmap, CanvasRenderTarget
from win32more.Microsoft.Graphics.Canvas.Geometry import (
    CanvasCapStyle,
    CanvasDashStyle,
    CanvasFigureLoop,
    CanvasFilledRegionDetermination,
    CanvasGeometry,
    CanvasLineJoin,
    CanvasPathBuilder,
    CanvasStrokeStyle,
)
from win32more.Microsoft.Graphics.Canvas.Text import CanvasTextFormat, CanvasTextLayout
from win32more.Microsoft.Graphics.Canvas.UI.Xaml import CanvasControl
from win32more.Windows.Foundation import AsyncStatus, Rect
from win32more.Windows.Foundation.Numerics import Matrix3x2, Vector2

from toga.colors import rgb
from toga.constants import TRANSPARENT, Baseline, FillRule
from toga.fonts import SYSTEM, SYSTEM_DEFAULT_FONT_SIZE
from toga.handlers import WeakrefCallable
from toga.widgets.canvas.geometry import arc_to_bezier, round_rect, sweepangle

from ..colors import native_color
from ..libs.png import png_from_rgba
from .base import Widget

logger = logging.getLogger(__name__)
BLACK = native_color(rgb(0, 0, 0))
IDENTITY = (1, 0, 0, 1, 0, 0)


def vector2(x, y):
    vector = Vector2()
    vector.X = x
    vector.Y = y
    return vector


def rect(x, y, width, height):
    native = Rect()
    native.X = x
    native.Y = y
    native.Width = width
    native.Height = height
    return native


def native_matrix(matrix):
    native = Matrix3x2()
    native.M11, native.M12, native.M21, native.M22, native.M31, native.M32 = matrix
    return native


def multiply(first, second):
    a1, b1, c1, d1, e1, f1 = first
    a2, b2, c2, d2, e2, f2 = second
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def transform_point(matrix, x, y):
    a, b, c, d, e, f = matrix
    return (a * x + c * y + e, b * x + d * y + f)


class State:
    def __init__(self, previous=None):
        if previous is None:
            self.fill_color = BLACK
            self.stroke_color = BLACK
            self.line_width = 2.0
            self.line_dash = []
            self.transform = IDENTITY
            self.singular = False
        else:
            self.fill_color = previous.fill_color
            self.stroke_color = previous.stroke_color
            self.line_width = previous.line_width
            self.line_dash = list(previous.line_dash)
            self.transform = previous.transform
            self.singular = previous.singular


class Figure:
    def __init__(self, start):
        self.start = start
        self.commands = []
        self.closed = False

    @property
    def current_point(self):
        if not self.commands:
            return self.start

        command, points = self.commands[-1]
        if command == "line":
            return points
        return points[-1]


class Context:
    def __init__(self, impl, native):
        self.impl = impl
        self.native = native
        self.resource_creator = native.Device
        self.states = [State()]
        self.begin_path()

        # Backwards compatibility for Toga <= 0.5.3.
        self.in_fill = False
        self.in_stroke = False

    @property
    def state(self):
        return self.states[-1]

    @property
    def current_figure(self):
        return self.figures[-1] if self.figures else None

    def save(self):
        self.states.append(State(self.state))

    def restore(self):
        if len(self.states) > 1:
            self.states.pop()

    def set_fill_style(self, color):
        self.state.fill_color = native_color(color)

    def set_line_dash(self, line_dash):
        if line_dash and len(line_dash) % 2:
            line_dash = line_dash * 2
        self.state.line_dash = list(line_dash or [])

    def set_line_width(self, line_width):
        self.state.line_width = line_width

    def set_stroke_style(self, color):
        self.state.stroke_color = native_color(color)

    def begin_path(self):
        self.figures = []

    def close_path(self):
        if figure := self.current_figure:
            figure.closed = True

    def move_to(self, x, y):
        self.figures.append(Figure(transform_point(self.state.transform, x, y)))

    def line_to(self, x, y):
        point = transform_point(self.state.transform, x, y)
        if figure := self.current_figure:
            figure.commands.append(("line", point))
        else:
            self.figures.append(Figure(point))

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y):
        if self.current_figure is None:
            self.move_to(cp1x, cp1y)

        self.current_figure.commands.append(
            (
                "cubic",
                (
                    transform_point(self.state.transform, cp1x, cp1y),
                    transform_point(self.state.transform, cp2x, cp2y),
                    transform_point(self.state.transform, x, y),
                ),
            )
        )

    def quadratic_curve_to(self, cpx, cpy, x, y):
        if self.current_figure is None:
            self.move_to(cpx, cpy)

        self.current_figure.commands.append(
            (
                "quadratic",
                (
                    transform_point(self.state.transform, cpx, cpy),
                    transform_point(self.state.transform, x, y),
                ),
            )
        )

    def arc(self, x, y, radius, startangle, endangle, counterclockwise):
        self.ellipse(x, y, radius, radius, 0, startangle, endangle, counterclockwise)

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
        ellipse_transform = multiply(
            multiply(
                multiply(
                    multiply((1, 0, 0, 1, x, y), self._rotation(rotation)),
                    (radiusx, 0, 0, radiusy, 0, 0),
                ),
                self._rotation(startangle),
            ),
            IDENTITY,
        )
        points = [
            transform_point(
                self.state.transform,
                *transform_point(ellipse_transform, px, py),
            )
            for px, py in arc_to_bezier(
                sweepangle(startangle, endangle, counterclockwise)
            )
        ]

        start = points.pop(0)
        if self.current_figure is None:
            self.figures.append(Figure(start))
        else:
            self.current_figure.commands.append(("line", start))

        for index in range(0, len(points), 3):
            self.current_figure.commands.append(
                ("cubic", tuple(points[index : index + 3]))
            )

    def rect(self, x, y, width, height):
        points = [
            transform_point(self.state.transform, x, y),
            transform_point(self.state.transform, x + width, y),
            transform_point(self.state.transform, x + width, y + height),
            transform_point(self.state.transform, x, y + height),
        ]
        figure = Figure(points[0])
        for point in points[1:]:
            figure.commands.append(("line", point))
        figure.closed = True
        self.figures.append(figure)

    def round_rect(self, x, y, width, height, radii):
        round_rect(self, x, y, width, height, radii)

    def fill(self, fill_rule):
        if self.state.singular:
            return

        if geometry := self._geometry(fill_rule):
            self.native.FillGeometryAtOriginWithColor(geometry, self.state.fill_color)

    def stroke(self):
        if self.state.singular:
            return

        geometry = self._dashed_geometry() if self.state.line_dash else self._geometry()
        if geometry:
            self.native.DrawGeometryAtOriginWithColorAndStrokeWidthAndStrokeStyle(
                geometry,
                self.state.stroke_color,
                self.state.line_width,
                self._stroke_style(),
            )

    def _dashed_geometry(self):
        builder = CanvasPathBuilder.Create(self.resource_creator)
        pattern = [dash for dash in self.state.line_dash if dash > 0]
        if not pattern:
            return self._geometry()

        for figure in self.figures:
            points = [figure.start]
            for command, command_points in figure.commands:
                if command != "line":
                    return self._geometry()
                points.append(command_points)

            if figure.closed:
                points.append(figure.start)

            dash_index = 0
            dash_remaining = pattern[dash_index]
            dash_on = True

            for start, end in zip(points, points[1:], strict=False):
                x1, y1 = start
                x2, y2 = end
                length = math.hypot(x2 - x1, y2 - y1)
                if length == 0:
                    continue

                position = 0
                while position < length:
                    step = min(dash_remaining, length - position)
                    if dash_on and step > 0:
                        segment_start = position / length
                        segment_end = (position + step) / length
                        builder.BeginFigureAtCoords(
                            x1 + (x2 - x1) * segment_start,
                            y1 + (y2 - y1) * segment_start,
                        )
                        builder.AddLineWithCoords(
                            x1 + (x2 - x1) * segment_end,
                            y1 + (y2 - y1) * segment_end,
                        )
                        builder.EndFigure(CanvasFigureLoop.Open)

                    position += step
                    dash_remaining -= step
                    if dash_remaining <= 0:
                        dash_index = (dash_index + 1) % len(pattern)
                        dash_remaining = pattern[dash_index]
                        dash_on = dash_index % 2 == 0

        return CanvasGeometry.CreatePath(builder)

    def _geometry(self, fill_rule=FillRule.NONZERO):
        if not self.figures:
            return None

        builder = CanvasPathBuilder.Create(self.resource_creator)
        if fill_rule == FillRule.EVENODD:
            builder.SetFilledRegionDetermination(CanvasFilledRegionDetermination.Alternate)
        else:
            builder.SetFilledRegionDetermination(CanvasFilledRegionDetermination.Winding)

        for figure in self.figures:
            builder.BeginFigureAtCoords(*figure.start)
            for command, points in figure.commands:
                if command == "line":
                    builder.AddLineWithCoords(*points)
                elif command == "cubic":
                    builder.AddCubicBezier(*(vector2(*point) for point in points))
                else:
                    builder.AddQuadraticBezier(*(vector2(*point) for point in points))

            builder.EndFigure(
                CanvasFigureLoop.Closed if figure.closed else CanvasFigureLoop.Open
            )

        return CanvasGeometry.CreatePath(builder)

    def _stroke_style(self):
        style = CanvasStrokeStyle()
        style.StartCap = CanvasCapStyle.Flat
        style.EndCap = CanvasCapStyle.Flat
        style.LineJoin = CanvasLineJoin.Miter
        style.MiterLimit = 10
        style.DashStyle = CanvasDashStyle.Solid
        return style

    def _rotation(self, radians):
        cos = math.cos(radians)
        sin = math.sin(radians)
        return (cos, sin, -sin, cos, 0, 0)

    @contextmanager
    def _native_transform(self, matrix):
        previous = self.native.Transform
        self.native.Transform = native_matrix(matrix)
        try:
            yield
        finally:
            self.native.Transform = previous

    def rotate(self, radians):
        self.state.transform = multiply(self.state.transform, self._rotation(radians))

    def scale(self, sx, sy):
        if sx == 0:
            sx = 2**-24
            self.state.singular = True
        if sy == 0:
            sy = 2**-24
            self.state.singular = True

        self.state.transform = multiply(self.state.transform, (sx, 0, 0, sy, 0, 0))

    def translate(self, tx, ty):
        self.state.transform = multiply(self.state.transform, (1, 0, 0, 1, tx, ty))

    def reset_transform(self):
        self.state.transform = IDENTITY
        self.state.singular = False

    def write_text(self, text, x, y, font, baseline, line_height):
        if self.state.singular or not text:
            return

        format = CanvasTextFormat()
        format.FontFamily = font.native_family.Source
        format.FontSize = font.native_size
        format.FontWeight = font.native_weight
        format.FontStyle = font.native_style

        if line_height is not None:
            format.LineSpacing = font.native_size * line_height

        layout = CanvasTextLayout.Create(
            self.resource_creator,
            text,
            format,
            10000,
            10000,
        )
        bounds = layout.LayoutBounds
        text_height = bounds.Height

        if baseline == Baseline.TOP:
            top = y
        elif baseline == Baseline.MIDDLE:
            top = y - text_height / 2
        elif baseline == Baseline.BOTTOM:
            top = y - text_height
        else:
            top = y - (font.native_size * 0.8)

        transform = multiply(self.state.transform, (1, 0, 0, 1, x, top))
        with self._native_transform(transform):
            if self.in_fill:
                self.native.DrawTextLayoutAtCoordsWithColor(
                    layout,
                    0,
                    0,
                    self.state.fill_color,
                )
            if self.in_stroke:
                geometry = CanvasGeometry.CreateText(layout)
                self.native.DrawGeometryAtOriginWithColorAndStrokeWidth(
                    geometry,
                    self.state.stroke_color,
                    self.state.line_width,
                )

    def draw_image(self, image, x, y, width, height):
        if self.state.singular:
            return

        bitmap = self.impl._canvas_bitmap(image)
        with self._native_transform(self.state.transform):
            self.native.DrawImageToRect(bitmap, rect(x, y, width, height))



class Canvas(Widget):
    def create(self):
        self.native = CanvasControl()
        self.native.IsTabStop = False
        self.native.Draw += WeakrefCallable(self.native_event_draw)
        self._width = 0
        self._height = 0
        self._bitmap_cache = {}

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    def set_background_color(self, color):
        super().set_background_color(color)
        self.native.ClearColor = native_color(color or TRANSPARENT)
        self.native.Invalidate()

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
        target = CanvasRenderTarget.CreateWithWidthAndHeightAndDpi(
            self.native.Device,
            width,
            height,
            self.native.Dpi,
        )
        session = target.CreateDrawingSession()
        try:
            self._render(session)
        finally:
            session.Close()

        return self._png(
            target.SizeInPixels.Width,
            target.SizeInPixels.Height,
            target.GetPixelBytes(),
        )

    def _png(self, width, height, bgra):
        rgba = bytearray()
        for row in range(height):
            for column in range(width):
                offset = ((row * width) + column) * 4
                b, g, r, a = bgra[offset:offset + 4]
                if a:
                    r = min(255, round(r * 255 / a))
                    g = min(255, round(g * 255 / a))
                    b = min(255, round(b * 255 / a))
                rgba.extend((r, g, b, a))

        return png_from_rgba(width, height, rgba)

    def _canvas_bitmap(self, image):
        path = image._impl.native.path
        try:
            return self._bitmap_cache[path]
        except KeyError:
            loaded = {}
            event = Event()
            operation = CanvasBitmap.LoadAsyncFromHstring(self.native.Device, str(path))

            def completed(async_info, async_status):
                if async_status == AsyncStatus.Completed:
                    loaded["bitmap"] = async_info.GetResults()
                event.set()

            operation.Completed = completed
            event.wait()
            bitmap = loaded["bitmap"]
            self._bitmap_cache[path] = bitmap
            return bitmap

    def _render(self, drawing_session):
        drawing_session.Clear(
            native_color(self.interface.style.background_color or TRANSPARENT)
        )
        context = Context(self, drawing_session)
        self.interface.root_state._draw(context)

    def native_event_draw(self, sender, args):
        try:
            self._render(args.DrawingSession)
        except Exception:
            logger.exception("Error rendering Canvas.")

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
