import re
from string import ascii_lowercase

from win32more.Windows.System import VirtualKey, VirtualKeyModifiers

from toga.keys import Key

WINUI_MODIFIERS = {
    Key.MOD_1: VirtualKeyModifiers.Control,
    Key.MOD_2: VirtualKeyModifiers.Menu,
    Key.MOD_3: VirtualKeyModifiers.Windows,
    Key.SHIFT: VirtualKeyModifiers.Shift,
}

WINUI_KEYS = {
    Key.ESCAPE.value: VirtualKey.Escape,
    Key.BACK_QUOTE.value: VirtualKey(0xC0),
    Key.MINUS.value: VirtualKey(0xBD),
    Key.EQUAL.value: VirtualKey(0xBB),
    Key.CAPSLOCK.value: VirtualKey.CapitalLock,
    Key.TAB.value: VirtualKey.Tab,
    Key.OPEN_BRACKET.value: VirtualKey(0xDB),
    Key.CLOSE_BRACKET.value: VirtualKey(0xDD),
    Key.BACKSLASH.value: VirtualKey(0xDC),
    Key.SEMICOLON.value: VirtualKey(0xBA),
    Key.QUOTE.value: VirtualKey(0xDE),
    Key.COMMA.value: VirtualKey(0xBC),
    Key.FULL_STOP.value: VirtualKey(0xBE),
    Key.SLASH.value: VirtualKey(0xBF),
    Key.SPACE.value: VirtualKey.Space,
    Key.BACKSPACE.value: VirtualKey.Back,
    Key.ENTER.value: VirtualKey.Enter,
    Key.PAGE_UP.value: VirtualKey.PageUp,
    Key.PAGE_DOWN.value: VirtualKey.PageDown,
    Key.INSERT.value: VirtualKey.Insert,
    Key.DELETE.value: VirtualKey.Delete,
    Key.HOME.value: VirtualKey.Home,
    Key.END.value: VirtualKey.End,
    Key.UP.value: VirtualKey.Up,
    Key.DOWN.value: VirtualKey.Down,
    Key.LEFT.value: VirtualKey.Left,
    Key.RIGHT.value: VirtualKey.Right,
    Key.NUMLOCK.value: VirtualKey.NumberKeyLock,
    Key.NUMPAD_DECIMAL_POINT.value: VirtualKey.Decimal,
    Key.NUMPAD_DIVIDE.value: VirtualKey.Divide,
    Key.NUMPAD_ENTER.value: VirtualKey.Enter,
    Key.NUMPAD_MINUS.value: VirtualKey.Subtract,
    Key.NUMPAD_MULTIPLY.value: VirtualKey.Multiply,
    Key.NUMPAD_PLUS.value: VirtualKey.Add,
    Key.SCROLLLOCK.value: VirtualKey.Scroll,
    Key.MENU.value: VirtualKey.Application,
    Key.PAUSE.value: VirtualKey.Pause,
}
WINUI_KEYS.update(
    {letter: getattr(VirtualKey, letter.upper()) for letter in ascii_lowercase}
)
WINUI_KEYS.update(
    {str(digit): getattr(VirtualKey, f"Number{digit}") for digit in range(10)}
)
WINUI_KEYS.update(
    {
        getattr(Key, f"F{function_key}").value: getattr(
            VirtualKey,
            f"F{function_key}",
        )
        for function_key in range(1, 20)
    }
)
WINUI_KEYS.update(
    {
        getattr(Key, f"NUMPAD_{digit}").value: getattr(VirtualKey, f"NumberPad{digit}")
        for digit in range(10)
    }
)

SHIFTED_KEYS = dict(zip("!@#$%^&*()", "1234567890", strict=False))
SHIFTED_KEYS.update({lower.upper(): lower for lower in ascii_lowercase})
SHIFTED_KEYS.update(
    {
        "~": "`",
        "_": "-",
        "+": "=",
        "{": "[",
        "}": "]",
        "|": "\\",
        ":": ";",
        '"': "'",
        "<": ",",
        ">": ".",
        "?": "/",
    }
)

WINUI_TO_TOGA_KEYS = {
    (key.value if hasattr(key, "value") else key): value
    for value, key in WINUI_KEYS.items()
}


def _key_value(key):
    return key.value if hasattr(key, "value") else key


def toga_to_winui_key(key):
    try:
        key = key.value
    except AttributeError:
        pass

    modifiers = 0
    for modifier, modifier_code in WINUI_MODIFIERS.items():
        if modifier.value in key:
            modifiers |= modifier_code
            key = key.replace(modifier.value, "")

    if lower := SHIFTED_KEYS.get(key):
        key = lower
        modifiers |= VirtualKeyModifiers.Shift

    try:
        native_key = WINUI_KEYS[key]
    except KeyError:
        if match := re.fullmatch(r"<(.+)>", key):
            key = match[1]
        try:
            native_key = getattr(VirtualKey, key.title())
        except AttributeError:
            raise ValueError(f"unknown key: {key!r}") from None

    return native_key, VirtualKeyModifiers(modifiers)


def toga_to_winui_shortcut(key):
    try:
        key = key.value
    except AttributeError:
        pass

    display = []
    for toga_keyval, winui_keyval in [
        (Key.MOD_1.value, "Ctrl"),
        (Key.MOD_2.value, "Alt"),
        (Key.MOD_3.value, "Win"),
        (Key.SHIFT.value, "Shift"),
    ]:
        if toga_keyval in key:
            display.append(winui_keyval)
            key = key.replace(toga_keyval, "")

    if key == " ":
        display.append("Space")
    else:
        if match := re.fullmatch(r"<(.+)>", key):
            key = match[1]
        display.append(key.title())

    return "+".join(display)


def winui_to_toga_key(native_key, native_modifiers):
    modifiers = set()
    native_modifiers = _key_value(native_modifiers)
    for toga_mod, native_mod in WINUI_MODIFIERS.items():
        if native_modifiers & native_mod:
            modifiers.add(toga_mod)

    key_value = WINUI_TO_TOGA_KEYS.get(_key_value(native_key))
    if key_value is None:
        raise ValueError(f"unknown key: {native_key!r}")

    if (Key.SHIFT in modifiers) and (key_value not in ascii_lowercase):
        for symbol, base in SHIFTED_KEYS.items():
            if base == key_value:
                key_value = symbol
                modifiers.remove(Key.SHIFT)
                break

    return {"key": Key(key_value), "modifiers": modifiers}
