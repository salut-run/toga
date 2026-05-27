import pytest
from pytest import approx
from win32more.Microsoft.UI.Xaml.Media import SolidColorBrush

from toga.colors import TRANSPARENT, rgb
from toga.style.pack import JUSTIFY, LEFT

from ..probe import BaseProbe


def toga_color(brush):
    if brush is None:
        return None

    try:
        brush = brush.as_(SolidColorBrush)
    except (AttributeError, OSError, TypeError):
        pass

    if not isinstance(brush, SolidColorBrush):
        return None

    color = brush.Color
    if color.A == 0 and color.R == 0 and color.G == 0 and color.B == 0:
        return TRANSPARENT

    return rgb(color.R, color.G, color.B, color.A / 255)


class SimpleProbe(BaseProbe):
    invalid_size_while_hidden = False

    def __init__(self, widget):
        self.app = widget.app
        self.widget = widget
        self.impl = widget._impl
        super().__init__(self.impl.native)
        assert isinstance(self.native, self.native_class)

    def assert_container(self, container):
        assert self.widget._impl.container is container._impl.container
        assert self.impl in container._impl.container.widgets._widgets

    def assert_not_contained(self):
        assert self.widget._impl.container is None

    def assert_text_align(self, expected):
        actual = self.text_align
        if expected == JUSTIFY:
            assert actual == LEFT
        else:
            assert actual == expected

    @property
    def enabled(self):
        if hasattr(self.native, "IsEnabled"):
            return self.native.IsEnabled
        return self.impl.get_enabled()

    @property
    def color(self):
        if hasattr(self.native, "Foreground"):
            return toga_color(self.native.Foreground)
        return None

    @property
    def background_color(self):
        if hasattr(self.native, "Background"):
            return toga_color(self.native.Background)
        return None

    @property
    def hidden(self):
        return self.native.Visibility != 0

    @property
    def shrink_on_resize(self):
        return True

    def assert_layout(self, size, position):
        assert self.widget._impl.container is not None
        assert (self.width, self.height) == approx(size, abs=1)
        assert (self.x, self.y) == approx(position, abs=1)

    async def press(self):
        self.native_event_click(None, None)

    @property
    def is_hidden(self):
        return self.hidden

    @property
    def has_focus(self):
        return self.impl.has_focus

    async def undo(self):
        pytest.skip("Undo not supported on this platform")

    async def redo(self):
        pytest.skip("Redo not supported on this platform")

    def native_event_click(self, sender, args):
        self.impl.native_event_click(sender, args)
