from win32more.Microsoft.UI.Xaml.Controls import Border, Image as NativeImageView
from win32more.Microsoft.UI.Xaml.Media import Stretch

from toga.widgets.imageview import rehint_imageview

from ..colors import native_brush
from .base import Widget


class ImageView(Widget):
    def create(self):
        self.native = Border()
        self.native_image = NativeImageView()
        self.native.Child = self.native_image
        self.native_image.Stretch = Stretch.Fill

    def set_image(self, image):
        if image:
            self.native_image.Source = image._impl.native.bitmap
        else:
            self.native_image.Source = None

    def set_background_color(self, color):
        if color is None:
            self.native.ClearValue(Border.BackgroundProperty)
        else:
            self.native.Background = native_brush(color)

    def get_enabled(self):
        return True

    def set_enabled(self, value):
        pass

    @property
    def has_focus(self):
        return False

    def focus(self):
        pass

    def rehint(self):
        width, height, aspect_ratio = rehint_imageview(
            self.interface.image,
            self.interface.style,
        )
        self.interface.intrinsic.width = width
        self.interface.intrinsic.height = height
        self.native_image.Stretch = (
            Stretch.Uniform if aspect_ratio is not None else Stretch.Fill
        )
