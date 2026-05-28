from io import BytesIO

from PIL import Image
from win32more.Microsoft.Graphics.Canvas.UI.Xaml import CanvasControl

from .base import SimpleProbe


class CanvasProbe(SimpleProbe):
    native_class = CanvasControl

    def reference_variant(self, reference):
        return {
            "attributes": "attributes-winui3",
            "miter_join": "miter_join-winforms",
            "transforms_mid_path": "transforms_mid_path-winui3",
        }.get(reference, reference)

    def get_image(self):
        return self.get_exported_image()

    def get_exported_image(self):
        return Image.open(BytesIO(self.impl.get_image_data()))

    async def mouse_press(self, x, y, **kwargs):
        self.impl.simulate_press(x, y)

    async def mouse_activate(self, x, y, **kwargs):
        self.impl.simulate_activate(x, y)

    async def mouse_drag(self, x1, y1, x2, y2, **kwargs):
        self.impl.simulate_drag(x1, y1, x2, y2)

    async def alt_mouse_press(self, x, y):
        self.impl.simulate_alt_press(x, y)

    async def alt_mouse_drag(self, x1, y1, x2, y2):
        self.impl.simulate_alt_drag(x1, y1, x2, y2)
