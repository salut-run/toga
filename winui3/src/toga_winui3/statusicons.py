from ctypes import byref, sizeof
from itertools import count

from win32more.Windows.Win32.Foundation import POINT, RECT
from win32more.Windows.Win32.System.LibraryLoader import GetModuleHandleW
from win32more.Windows.Win32.UI import Shell
from win32more.Windows.Win32.UI.WindowsAndMessaging import (
    MF_POPUP,
    MF_SEPARATOR,
    MF_STRING,
    TPM_NONOTIFY,
    TPM_RETURNCMD,
    TPM_RIGHTBUTTON,
    WM_CONTEXTMENU,
    WM_LBUTTONUP,
    WM_NULL,
    WM_RBUTTONUP,
    WM_USER,
    WNDCLASSW,
    WNDPROC,
    AppendMenuW,
    CreatePopupMenu,
    CreateWindowExW,
    DefWindowProcW,
    DestroyMenu,
    DestroyWindow,
    GetCursorPos,
    PostMessageW,
    RegisterClassW,
    RegisterWindowMessageW,
    SetForegroundWindow,
    TrackPopupMenu,
)

import toga
from toga.command import Group, Separator

WM_STATUS_ICON = WM_USER + 1
WM_TASKBAR_CREATED = RegisterWindowMessageW("TaskbarCreated")
NIN_KEYSELECT = Shell.NIN_SELECT + 1

_ICON_IDS = count(1)
_MENU_IDS = count(1000)


class StatusIcon:
    def __init__(self, interface):
        self.interface = interface
        self.native = None
        self.icon = None
        self._id = next(_ICON_IDS)
        self._callback = None
        self._hwnd = None
        self._notify_data = None
        self._menu = None
        self._menu_commands = {}

    def set_icon(self, icon):
        self.icon = icon
        if self.native:
            self._modify()

    def create(self):
        self._create_message_window()
        self._add()
        self.native = self._hwnd

    def remove(self):
        if self.native:
            Shell.Shell_NotifyIconW(Shell.NIM_DELETE, byref(self._notify_data))
        if self._hwnd:
            DestroyWindow(self._hwnd)
        self._destroy_menu()
        self.native = None
        self._hwnd = None
        self._notify_data = None

    def has_native_icon(self):
        return self.native_icon_rect() is not None

    def native_icon_rect(self):
        if not self.native:
            return None

        identifier = Shell.NOTIFYICONIDENTIFIER()
        identifier.cbSize = sizeof(Shell.NOTIFYICONIDENTIFIER)
        identifier.hWnd = self._hwnd
        identifier.uID = self._id

        rect = RECT()
        if Shell.Shell_NotifyIconGetRect(byref(identifier), byref(rect)) == 0:
            return rect
        return None

    @property
    def _native_icon(self):
        icon = self.icon or toga.App.app.icon
        return icon._impl.handle

    def _create_message_window(self):
        def wndproc(hwnd, msg, wparam, lparam):
            if msg == WM_STATUS_ICON:
                self._handle_status_message(lparam)
                return 0
            elif msg == WM_TASKBAR_CREATED:
                self._restore_after_taskbar_created()
                return 0
            return DefWindowProcW(hwnd, msg, wparam, lparam)

        self._callback = WNDPROC(wndproc)
        instance = GetModuleHandleW(None)
        class_name = f"TogaWinUI3StatusIcon-{self._id}"

        wndclass = WNDCLASSW()
        wndclass.lpfnWndProc = self._callback
        wndclass.hInstance = instance
        wndclass.lpszClassName = class_name
        RegisterClassW(wndclass)

        self._hwnd = CreateWindowExW(
            0,
            class_name,
            class_name,
            0,
            0,
            0,
            0,
            0,
            None,
            None,
            instance,
            None,
        )

    def _notify_icon_data(self):
        data = Shell.NOTIFYICONDATAW()
        data.cbSize = sizeof(Shell.NOTIFYICONDATAW)
        data.hWnd = self._hwnd
        data.uID = self._id
        data.uFlags = Shell.NIF_MESSAGE | Shell.NIF_ICON | Shell.NIF_TIP
        data.uCallbackMessage = WM_STATUS_ICON
        data.hIcon = self._native_icon
        data.szTip = self.interface.text[:127]
        return data

    def _add(self):
        self._notify_data = self._notify_icon_data()
        Shell.Shell_NotifyIconW(Shell.NIM_ADD, byref(self._notify_data))
        self._notify_data.uVersion = Shell.NOTIFYICON_VERSION_4
        Shell.Shell_NotifyIconW(Shell.NIM_SETVERSION, byref(self._notify_data))

    def _modify(self):
        self._notify_data = self._notify_icon_data()
        Shell.Shell_NotifyIconW(Shell.NIM_MODIFY, byref(self._notify_data))

    def _restore_after_taskbar_created(self):
        if self.native:
            self._add()

    def _simulate_taskbar_restart(self):
        Shell.Shell_NotifyIconW(Shell.NIM_DELETE, byref(self._notify_data))
        PostMessageW(self._hwnd, WM_TASKBAR_CREATED, 0, 0)

    def _handle_status_message(self, message):
        if message in {WM_LBUTTONUP, Shell.NIN_SELECT, NIN_KEYSELECT}:
            self.winui_click()
        elif message in {WM_RBUTTONUP, WM_CONTEXTMENU}:
            self.show_menu()

    def _destroy_menu(self):
        if self._menu:
            DestroyMenu(self._menu)
        self._menu = None
        self._menu_commands = {}

    def _set_native_menu(self, menu, commands):
        self._destroy_menu()
        self._menu = menu
        self._menu_commands = commands

    def show_menu(self):
        if not self._menu:
            return

        point = POINT()
        GetCursorPos(byref(point))
        SetForegroundWindow(self._hwnd)
        command_id = TrackPopupMenu(
            self._menu,
            TPM_RIGHTBUTTON | TPM_RETURNCMD | TPM_NONOTIFY,
            point.x,
            point.y,
            0,
            self._hwnd,
            None,
        )
        if command := self._menu_commands.get(command_id):
            command.action()
        PostMessageW(self._hwnd, WM_NULL, 0, 0)


class SimpleStatusIcon(StatusIcon):
    def winui_click(self):
        self.interface.on_press()


class MenuStatusIcon(StatusIcon):
    def create(self):
        super().create()
        self.menu = []

    def winui_click(self):
        self.show_menu()


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
            item._impl._set_native_menu(*self._build_native_menu([]))

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

        for item in self.interface._menu_status_icons:
            item._impl._set_native_menu(*self._build_native_menu(item._impl.menu))

    def _build_native_menu(self, menu):
        native_menu = CreatePopupMenu()
        commands = {}

        for item in menu:
            if item["text"] == "---":
                AppendMenuW(native_menu, MF_SEPARATOR, 0, None)
            elif children := item.get("children"):
                submenu, child_commands = self._build_native_menu(children)
                AppendMenuW(native_menu, MF_POPUP, submenu, item["text"])
                commands.update(child_commands)
            else:
                command_id = next(_MENU_IDS)
                commands[command_id] = item["command"]
                AppendMenuW(native_menu, MF_STRING, command_id, item["text"])

        return native_menu, commands
