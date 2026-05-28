from win32more.Microsoft.UI.Xaml.Controls import PasswordBox, PasswordRevealMode

from toga.handlers import WeakrefCallable

from .base import native_horizontal_alignment
from .textinput import TextInput


class PasswordInput(TextInput):
    def create(self):
        self.native = PasswordBox()
        self.native.PasswordRevealMode = PasswordRevealMode.Hidden
        self.native.IsPasswordRevealButtonEnabled = False
        self.native.PasswordChanged += WeakrefCallable(
            self.native_event_password_changed
        )
        self.native.GotFocus += WeakrefCallable(self.native_event_got_focus)
        self.native.LostFocus += WeakrefCallable(self.native_event_lost_focus)
        self.native.KeyDown += WeakrefCallable(self.native_event_key_down)
        self._is_valid = True
        self._ignore_password_changed_value = None
        self._previous_password = ""
        self._readonly = False
        self._focus_reported = False

    def get_readonly(self):
        return self._readonly

    def set_readonly(self, value):
        self._readonly = value

    def get_value(self):
        return self.native.Password

    def set_value(self, value):
        if self.native.Password != value:
            self._ignore_password_changed_value = value
            self.native.Password = value
            self._previous_password = value
            self.interface._value_changed()

    def set_text_align(self, value):
        super().set_text_align(value)
        self.native.HorizontalContentAlignment = native_horizontal_alignment(value)

    def native_event_password_changed(self, sender, args):
        if self._ignore_password_changed_value == self.native.Password:
            self._ignore_password_changed_value = None
            self._previous_password = self.native.Password
        elif self._readonly:
            self._ignore_password_changed_value = self._previous_password
            self.native.Password = self._previous_password
        else:
            self._ignore_password_changed_value = None
            self._previous_password = self.native.Password
            self.interface._value_changed()
