from hashlib import sha1
from pathlib import Path

from win32more.Microsoft.UI.Xaml.Media.Imaging import BitmapImage
from win32more.Windows.Foundation import Uri

import toga
from toga.images import ImageLoadError

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class NativeImage:
    def __init__(self, data, width, height):
        self.data = data
        self.width = width
        self.height = height

        image_dir = toga.App.app.paths.cache / "toga" / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        image_path = image_dir / f"{sha1(data).hexdigest()}.png"
        if not image_path.exists():
            image_path.write_bytes(data)

        self.path = image_path
        self.bitmap = BitmapImage()
        self.bitmap.UriSource = Uri(image_path.as_uri())


class Image:
    RAW_TYPE = NativeImage

    def __init__(self, interface, data=None, raw=None):
        self.interface = interface

        if data is not None:
            data = bytes(data)
            width, height = self._png_size(data)
            self.native = NativeImage(data, width, height)
        else:
            self.native = raw

    def _png_size(self, data):
        if len(data) < 24 or not data.startswith(PNG_SIGNATURE):
            raise ImageLoadError

        return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

    def get_width(self):
        return self.native.width

    def get_height(self):
        return self.native.height

    def get_data(self):
        return self.native.data

    def save(self, path):
        path = Path(path)
        if path.suffix.lower() != ".png":
            raise ValueError(f"Don't know how to save image of type {path.suffix!r}")

        path.write_bytes(self.get_data())
