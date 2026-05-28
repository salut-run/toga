from win32more.Microsoft.UI.Xaml.Controls import Grid

from .base import SimpleProbe


class SplitContainerProbe(SimpleProbe):
    native_class = Grid
    border_size = 0
    direction_change_preserves_position = False

    def move_split(self, position):
        self.impl.set_split_position(position)

    async def wait_for_split(self):
        pass
