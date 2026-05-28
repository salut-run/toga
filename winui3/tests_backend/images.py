from toga_winui3.images import NativeImage

from .probe import BaseProbe


class ImageProbe(BaseProbe):
    def __init__(self, app, image):
        super().__init__()
        self.app = app
        self.image = image
        assert isinstance(self.image._impl.native, NativeImage)

    def supports_extension(self, extension):
        return extension.lower() == ".png"
