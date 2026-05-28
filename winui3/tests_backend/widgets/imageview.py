from win32more.Microsoft.UI.Xaml.Controls import Border, Image
from win32more.Microsoft.UI.Xaml.Media import Stretch

from .base import SimpleProbe


class ImageViewProbe(SimpleProbe):
    native_class = Border

    def __init__(self, widget):
        super().__init__(widget)
        self.native_image = self.impl.native_image
        assert isinstance(self.native_image, Image)

    @property
    def preserve_aspect_ratio(self):
        return self.native_image.Stretch == Stretch.Uniform

    def assert_image_size(self, width, height):
        pass
