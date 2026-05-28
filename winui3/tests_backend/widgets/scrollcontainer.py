import asyncio
from time import time

from win32more.Microsoft.UI.Xaml.Controls import ScrollViewer

from .base import SimpleProbe


class ScrollContainerProbe(SimpleProbe):
    native_class = ScrollViewer
    scrollbar_inset = 0
    frame_inset = 0

    @property
    def native_content(self):
        return self.impl.native_content

    @property
    def has_content(self):
        return self.impl.content is not None

    @property
    def document_height(self):
        return round(self.impl._document_height)

    @property
    def document_width(self):
        return round(self.impl._document_width)

    async def scroll(self):
        if self.impl.get_vertical() and self.document_height > self.height:
            self.impl.set_position(0, 100)

    async def wait_for_scroll_completion(self):
        target_horizontal = self.impl._horizontal_position
        target_vertical = self.impl._vertical_position
        deadline = time() + 1

        while time() < deadline:
            if (
                abs(self.impl.native.HorizontalOffset - target_horizontal) <= 1
                and abs(self.impl.native.VerticalOffset - target_vertical) <= 1
            ):
                break
            await asyncio.sleep(0.05)
