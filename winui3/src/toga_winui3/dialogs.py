from win32more.Microsoft.UI.Xaml import TextWrapping
from win32more.Microsoft.UI.Xaml.Controls import (
    ContentDialog,
    ContentDialogButton,
    ContentDialogResult,
    StackPanel,
    TextBlock,
    TextBox,
)
from win32more.Windows.Foundation import AsyncStatus

import toga

TEST_RESULT_UNSET = object()


class BaseDialog:
    def __init__(self):
        self.native = None
        self.result = TEST_RESULT_UNSET
        self.pre_close_test_method = None

    def show(self, host_window, future):
        if self.result is not TEST_RESULT_UNSET:
            self._create_native(host_window)
            if self.pre_close_test_method:
                self.pre_close_test_method(self.interface)
            future.set_result(self.result)
        else:
            future.set_result(None)

    def _host_window(self, host_window):
        return host_window or toga.App.app.current_window or toga.App.app.main_window

    def _create_native(self, host_window):
        return None


class MessageDialog(BaseDialog):
    primary_text = None
    secondary_text = None
    close_text = "OK"
    default_button = ContentDialogButton.Close

    def __init__(self, title, message, results=None):
        super().__init__()
        self.title = title
        self.message = message
        self.results = results or {ContentDialogResult.None_: None}

    def show(self, host_window, future):
        self._create_native(host_window)

        if self.result is not TEST_RESULT_UNSET:
            if self.pre_close_test_method:
                self.pre_close_test_method(self.interface)
            future.set_result(self.result)
            return

        operation = self.native.ShowAsync()

        def completed(async_info, async_status):
            if async_status == AsyncStatus.Completed:
                result = self.results.get(async_info.GetResults(), None)
            else:
                result = None

            if not future.done():
                future.set_result(result)

        operation.Completed = completed

    def _create_native(self, host_window):
        content = TextBlock()
        content.Text = self.message
        content.TextWrapping = TextWrapping.Wrap

        self.native = ContentDialog()
        self.native.Title = self.title
        self.native.Content = content
        self.native.PrimaryButtonText = self.primary_text or ""
        self.native.SecondaryButtonText = self.secondary_text or ""
        self.native.CloseButtonText = self.close_text or ""
        self.native.DefaultButton = self.default_button
        self.native.XamlRoot = self._host_window(
            host_window
        )._impl.content_native.XamlRoot
        return self.native


class InfoDialog(MessageDialog):
    pass


class QuestionDialog(MessageDialog):
    primary_text = "Yes"
    secondary_text = "No"
    close_text = None
    default_button = ContentDialogButton.Primary

    def __init__(self, title, message):
        super().__init__(
            title,
            message,
            results={
                ContentDialogResult.Primary: True,
                ContentDialogResult.Secondary: False,
                ContentDialogResult.None_: False,
            },
        )


class ConfirmDialog(MessageDialog):
    primary_text = "OK"
    secondary_text = "Cancel"
    close_text = None
    default_button = ContentDialogButton.Primary

    def __init__(self, title, message):
        super().__init__(
            title,
            message,
            results={
                ContentDialogResult.Primary: True,
                ContentDialogResult.Secondary: False,
                ContentDialogResult.None_: False,
            },
        )


class ErrorDialog(MessageDialog):
    pass


class StackTraceDialog(MessageDialog):
    def __init__(self, title, message, content, retry):
        super().__init__(title, message)
        self.content = content
        self.retry = retry
        if retry:
            self.primary_text = "Retry"
            self.secondary_text = "Quit"
            self.close_text = None
            self.default_button = ContentDialogButton.Primary
            self.results = {
                ContentDialogResult.Primary: True,
                ContentDialogResult.Secondary: False,
                ContentDialogResult.None_: False,
            }

    def _create_native(self, host_window):
        panel = StackPanel()

        message = TextBlock()
        message.Text = self.message
        message.TextWrapping = TextWrapping.Wrap
        panel.Children.Append(message)

        content = TextBox()
        content.Text = self.content
        content.AcceptsReturn = True
        content.IsReadOnly = True
        content.Height = 220
        panel.Children.Append(content)

        self.native = ContentDialog()
        self.native.Title = self.title
        self.native.Content = panel
        self.native.PrimaryButtonText = self.primary_text or ""
        self.native.SecondaryButtonText = self.secondary_text or ""
        self.native.CloseButtonText = self.close_text or ""
        self.native.DefaultButton = self.default_button
        self.native.XamlRoot = self._host_window(
            host_window
        )._impl.content_native.XamlRoot
        return self.native


class SaveFileDialog(BaseDialog):
    def __init__(
        self,
        title,
        filename,
        initial_directory,
        file_types=None,
    ):
        super().__init__()
        self.title = title
        self.filename = filename
        self.initial_directory = initial_directory
        self.file_types = file_types


class OpenFileDialog(BaseDialog):
    def __init__(
        self,
        title,
        initial_directory,
        file_types,
        multiple_select,
    ):
        super().__init__()
        self.title = title
        self.initial_directory = initial_directory
        self.file_types = file_types
        self.multiple_select = multiple_select


class SelectFolderDialog(BaseDialog):
    def __init__(
        self,
        title,
        initial_directory,
        multiple_select,
    ):
        super().__init__()
        self.title = title
        self.initial_directory = initial_directory
        self.multiple_select = multiple_select
