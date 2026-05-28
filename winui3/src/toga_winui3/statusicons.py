from toga.command import Group, Separator


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
    def create(self):
        super().create()
        self.menu = []


class StatusIconSet:
    def __init__(self, interface):
        self.interface = interface
        self._menu_items = {}

    def _submenu(self, group, group_cache):
        try:
            return group_cache[group]
        except KeyError as exc:
            if group is None:
                raise ValueError("Unknown top level item") from exc

            parent_menu = self._submenu(group.parent, group_cache)
            submenu = {
                "text": group.text,
                "children": [],
            }
            parent_menu.append(submenu)
            group_cache[group] = submenu["children"]
            return submenu["children"]

    def create(self):
        for item in self.interface._menu_status_icons:
            item._impl.menu = []

        primary_group = self.interface._primary_menu_status_icon
        if primary_group is None:
            return

        group_cache = {
            item: item._impl.menu for item in self.interface._menu_status_icons
        }
        group_cache[Group.COMMANDS] = primary_group._impl.menu
        self._menu_items = {}

        for cmd in self.interface.commands:
            try:
                submenu = self._submenu(cmd.group, group_cache)
            except ValueError as exc:
                raise ValueError(
                    f"Command {cmd.text!r} does not belong to a current status icon "
                    "group."
                ) from exc

            if isinstance(cmd, Separator):
                submenu.append({"text": "---", "command": None})
            else:
                item = {"text": cmd.text, "command": cmd}
                submenu.append(item)
                self._menu_items[(cmd.group, cmd.text)] = item
