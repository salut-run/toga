from win32more.Microsoft.UI.Xaml.Controls import Slider
from win32more.Microsoft.UI.Xaml.Controls.Primitives import TickPlacement

from .base import SimpleProbe


class SliderProbe(SimpleProbe):
    native_class = Slider

    @property
    def position(self):
        return (self.native.Value - self._min) / (self._max - self._min)

    async def change(self, position):
        self.native.Value = self._min + (position * (self._max - self._min))

    @property
    def tick_count(self):
        if self.native.TickPlacement == TickPlacement.BottomRight:
            return self.impl._tick_count
        else:
            assert self.native.TickPlacement == TickPlacement.None_
            return None

    @property
    def _min(self):
        return self.native.Minimum

    @property
    def _max(self):
        return self.native.Maximum

    async def press(self):
        self.impl.native_event_pointer_pressed(None, None)

    async def release(self):
        self.impl.native_event_pointer_released(None, None)
