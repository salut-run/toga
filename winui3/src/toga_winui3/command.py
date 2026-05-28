import sys

from win32more.Microsoft.UI.Xaml.Input import KeyboardAccelerator

from toga import Command as StandardCommand, Group, Key
from toga.handlers import WeakrefCallable

from .keys import toga_to_winui_key, toga_to_winui_shortcut


class Command:
    def __init__(self, interface):
        self.interface = interface
        self.native = []

    @classmethod
    def standard(self, app, id):
        # ---- File menu -----------------------------------
        if id == StandardCommand.NEW:
            return {
                "text": "New",
                "shortcut": Key.MOD_1 + "n",
                "group": Group.FILE,
                "section": 0,
                "order": 0,
            }
        elif id == StandardCommand.OPEN:
            return {
                "text": "Open...",
                "shortcut": Key.MOD_1 + "o",
                "group": Group.FILE,
                "section": 0,
                "order": 10,
            }
        elif id == StandardCommand.SAVE:
            return {
                "text": "Save",
                "shortcut": Key.MOD_1 + "s",
                "group": Group.FILE,
                "section": 0,
                "order": 20,
            }
        elif id == StandardCommand.SAVE_AS:
            return {
                "text": "Save As...",
                "shortcut": Key.MOD_1 + "S",
                "group": Group.FILE,
                "section": 0,
                "order": 21,
            }
        elif id == StandardCommand.SAVE_ALL:
            return {
                "text": "Save All",
                "shortcut": Key.MOD_1 + Key.MOD_2 + "s",
                "group": Group.FILE,
                "section": 0,
                "order": 22,
            }
        elif id == StandardCommand.PREFERENCES:
            # Preferences should be towards the end of the File menu.
            return {
                "text": "Preferences",
                "group": Group.FILE,
                "section": sys.maxsize - 1,
            }
        elif id == StandardCommand.EXIT:
            # Quit should always be the last item, in a section on its own.
            return {
                "text": "Exit",
                "group": Group.FILE,
                "section": sys.maxsize,
            }
        # ---- Help menu -----------------------------------
        elif id == StandardCommand.VISIT_HOMEPAGE:
            return {
                "text": "Visit homepage",
                "enabled": app.home_page is not None,
                "group": Group.HELP,
            }
        elif id == StandardCommand.ABOUT:
            return {
                "text": f"About {app.formal_name}",
                "group": Group.HELP,
                "section": sys.maxsize,
            }

        raise ValueError(f"Unknown standard command {id!r}")

    def native_event_Click(self, sender, args):
        return self.interface.action()

    def native_event_AcceleratorInvoked(self, sender, args):
        if self.interface.enabled:
            self.interface.action()
            args.Handled = True

    def set_enabled(self, value):
        if self.native:
            for widget in self.native:
                widget.IsEnabled = self.interface.enabled
                for index in range(len(widget.KeyboardAccelerators)):
                    accelerator = widget.KeyboardAccelerators.GetAt(index)
                    accelerator.IsEnabled = self.interface.enabled

    def create_menu_item(self, NativeClass):
        item = NativeClass()
        item.Text = self.interface.text
        item.add_Click(self.native_event_Click)

        if self.interface.shortcut is not None:
            try:
                key, modifiers = toga_to_winui_key(self.interface.shortcut)
            except ValueError:
                pass
            else:
                accelerator = KeyboardAccelerator()
                accelerator.Key = key
                accelerator.Modifiers = modifiers
                accelerator.IsEnabled = self.interface.enabled
                accelerator.add_Invoked(
                    WeakrefCallable(self.native_event_AcceleratorInvoked)
                )
                item.KeyboardAccelerators.Append(accelerator)
                item.KeyboardAcceleratorTextOverride = toga_to_winui_shortcut(
                    self.interface.shortcut
                )

        item.IsEnabled = self.interface.enabled

        self.native.append(item)

        return item
