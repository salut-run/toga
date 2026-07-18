import warnings
from abc import ABC, abstractmethod
from math import nan

from travertino.constants import TRANSPARENT
from travertino.size import at_least
from win32more.Microsoft.UI.Xaml import (
    FocusState,
    HorizontalAlignment,
    TextAlignment,
    Visibility,
)
from win32more.Microsoft.UI.Xaml.Controls import Canvas, Control, Panel
from win32more.Windows.Foundation import Size

from toga.style.pack import CENTER, JUSTIFY, LEFT, RIGHT

from ..colors import native_brush
from ..libs.misc import is_based_on

DEFAULT_TAB_INDEX = 2**31 - 1
UNCONSTRAINED_SIZE = Size(10000, 10000)


def native_text_alignment(value):
    return {
        LEFT: TextAlignment.Left,
        CENTER: TextAlignment.Center,
        RIGHT: TextAlignment.Right,
        JUSTIFY: TextAlignment.Left,
    }[value]


def native_horizontal_alignment(value):
    return {
        LEFT: HorizontalAlignment.Left,
        CENTER: HorizontalAlignment.Center,
        RIGHT: HorizontalAlignment.Right,
        JUSTIFY: HorizontalAlignment.Left,
    }[value]


class SourceListenerCompatibility:
    """Compatibility aliases for the pre-0.5.4 source listener API."""

    SOURCE_SUPPORTS_PARENT = False

    def _warn_source_alias(self, name):
        warnings.warn(
            f"The {name}() method is deprecated. Use source_{name}() instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def clear(self):
        self._warn_source_alias("clear")
        self.source_clear()

    def insert(self, index, item, parent=None):
        self._warn_source_alias("insert")
        kwargs = {"index": index, "item": item}
        if self.SOURCE_SUPPORTS_PARENT:
            kwargs["parent"] = parent
        self.source_insert(**kwargs)

    def change(self, item):
        self._warn_source_alias("change")
        self.source_change(item=item)

    def remove(self, index, item, parent=None):
        self._warn_source_alias("remove")
        kwargs = {"index": index, "item": item}
        if self.SOURCE_SUPPORTS_PARENT:
            kwargs["parent"] = parent
        self.source_remove(**kwargs)


class WidgetStager:
    def __init__(self, widget):
        self.width = 0
        self.height = 0
        self.valid = False
        self._widget = widget
        self._widget_copy = None

    def invalidate(self):
        self.valid = False

    def ensure(self):
        if not self.valid:
            self.refresh()

    def refresh(self):
        self._widget_copy = type(self._widget)(None)
        self._widget.container.staging_area.add(self._widget_copy)
        self._widget_copy.set_native_content(self._widget.content_creator())
        if hasattr(self._widget, "_font"):
            self._widget_copy.set_font(self._widget._font)
        desired_size = self._widget_copy.measure_unconstrained()
        self.width = desired_size.Width
        self.height = desired_size.Height
        self.valid = True

        self._widget.rehint()
        self._widget.container.staging_area.remove(self._widget_copy)
        self._widget_copy = None


class Widget(ABC):
    ####################################################################################
    # Widget creation.
    ####################################################################################

    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self._container = None
        self._content = None
        self._constraints = None
        self.native = None

        self.create()

    @abstractmethod
    def create(self): ...

    def set_app(self, app):
        self.app = app

    def set_window(self, window):
        self.window = window

    ####################################################################################
    # Methods relating to the container.
    ####################################################################################

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container):
        if container:
            with container.staging_area.batch():
                if self._container:
                    self._container.widgets.remove(self)

                self._container = container
                container.widgets.add(self)
                if self._constraints:
                    self._constraints.ensure()

                for child in self.interface.children:
                    child._impl.container = container
        else:
            if self._container:
                self._container.widgets.remove(self)

            self._container = None
            for child in self.interface.children:
                child._impl.container = None

        self.rehint()

    ####################################################################################
    # Methods relating to children.
    ####################################################################################

    def add_child(self, child):
        child.container = self.container

    def insert_child(self, index, child):
        self.add_child(child)

    def remove_child(self, child):
        child.container = None

    ####################################################################################
    # Methods called by the Toga style applicator.
    ####################################################################################

    def set_background_color(self, color):
        cls_native = type(self.native)
        if color is None:
            if is_based_on(cls_native, Control):
                self.native.ClearValue(Control.BackgroundProperty)
            elif is_based_on(cls_native, Panel):
                self.native.Background = native_brush(TRANSPARENT)
            else:
                pass
        else:
            self.native.Background = native_brush(color)

    def set_bounds(self, x, y, width, height):
        self.native.Width = width
        self.native.Height = height
        Canvas.SetLeft(self.native, x)
        Canvas.SetTop(self.native, y)

    def set_color(self, color):
        cls_native = type(self.native)

        # WinUI 3 controls based on the Panel class do not have a Foreground property.
        if is_based_on(cls_native, Panel):
            return

        if color is None:
            if is_based_on(cls_native, Control):
                self.native.ClearValue(Control.ForegroundProperty)
            else:
                pass
        else:
            self.native.Foreground = native_brush(color)

    def set_font(self, font):
        self._font = font
        self._apply_font(self.native)
        if content := getattr(self, "content", None):
            self._apply_font(content)

        if self._constraints:
            self._constraints.invalidate()
            if self._container:
                self._constraints.refresh()

    def set_hidden(self, hidden):
        self.native.Visibility = Visibility.Collapsed if hidden else Visibility.Visible

    def set_text_align(self, alignment):
        self._text_align = alignment

    ####################################################################################
    # Other methods called by the Toga core interface.
    ####################################################################################

    def get_enabled(self):
        return self.native.IsEnabled

    def set_enabled(self, value):
        self.native.IsEnabled = value

    @property
    def has_focus(self):
        return self._focus_target.FocusState != FocusState.Unfocused

    @property
    def _focus_target(self):
        return self.native

    def focus(self):
        self._focus_target.Focus(FocusState.Programmatic)

    def get_tab_index(self):
        if self.native.TabIndex == DEFAULT_TAB_INDEX and self._container:
            if parent := self.interface.parent:
                return parent.children.index(self.interface) + 1
            return self._container.widgets._widgets.index(self) + 1
        return self.native.TabIndex

    def set_tab_index(self, tab_index):
        self.native.TabIndex = tab_index

    def refresh(self):
        self.rehint()

    def measure_unconstrained(self, native=None):
        native = self.native if native is None else native
        width = native.Width
        height = native.Height
        try:
            native.Width = nan
            native.Height = nan
            native.Measure(UNCONSTRAINED_SIZE)
            return native.DesiredSize
        finally:
            native.Width = width
            native.Height = height

    def rehint(self):
        self.interface.intrinsic.width = at_least(self.interface._MIN_WIDTH)
        self.interface.intrinsic.height = at_least(self.interface._MIN_HEIGHT)

    ####################################################################################
    # Content.
    #
    # These methods are to be used by Widgets that have minimum size constraints based
    # on their content. When these widgets are staged in the container staging area, a
    # copy of the native content needs to be created. It's difficult to created a direct
    # copy of the content, so here a mechanism is used to create a new version of the
    # content using a "content creator".
    ####################################################################################

    @property
    def content_creator(self):
        return self._content_creator

    @content_creator.setter
    def content_creator(self, creator):
        self._content_creator = creator
        self.content = creator()
        self.set_native_content(self.content)

        self._constraints.invalidate()
        if self._container:
            self._constraints.refresh()

    def set_native_content(self, content):
        self.native.Content = content
        if hasattr(self, "_font"):
            self._apply_font(content)

    def _apply_font(self, native):
        font_impl = self._font._impl
        for attr, value in [
            ("FontFamily", font_impl.native_family),
            ("FontSize", font_impl.native_size),
            ("FontWeight", font_impl.native_weight),
            ("FontStyle", font_impl.native_style),
        ]:
            if hasattr(native, attr):
                setattr(native, attr, value)
