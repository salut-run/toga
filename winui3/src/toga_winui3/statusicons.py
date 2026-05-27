class StatusIcon:
    def __init__(self, interface):
        self.interface = interface
        self.native = None
        self.icon = None

    def set_icon(self, icon):
        self.icon = icon

    def create(self):
        self.native = self

    def remove(self):
        self.native = None


class SimpleStatusIcon(StatusIcon):
    def winui_click(self):
        self.interface.on_press()


class MenuStatusIcon(StatusIcon):
    pass


class StatusIconSet:
    def __init__(self, interface):
        self.interface = interface
        self._menu_items = {}

    def create(self):
        pass
