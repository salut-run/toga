from pathlib import Path

from win32more import ComError
from win32more.Microsoft.UI.Xaml import TextWrapping
from win32more.Microsoft.UI.Xaml.Controls import (
    ContentDialog,
    ContentDialogButton,
    ContentDialogResult,
    StackPanel,
    TextBlock,
    TextBox,
)
from win32more.Microsoft.Windows.Storage.Pickers import (
    FileOpenPicker,
    FileSavePicker,
    FolderPicker,
    PickerLocationId,
    PickerViewMode,
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

    def _window_id(self, host_window):
        return self._host_window(host_window)._impl.native.AppWindow.Id

    def _create_native(self, host_window):
        return None

    def _set_future_result(self, future, result):
        def complete_future():
            if not future.done():
                future.set_result(result)

        if not future.done():
            future.get_loop().call_soon_threadsafe(complete_future)

    def _set_future_result_from_async_operation(self, operation, future, converter):
        self.operation = operation

        def completed(async_info, async_status):
            try:
                if async_status == AsyncStatus.Completed:
                    result = converter(async_info.GetResults())
                else:
                    result = None
            except Exception:
                result = None

            self._set_future_result(future, result)

        operation.Completed = completed


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

        self._set_future_result_from_async_operation(
            self.native.ShowAsync(),
            future,
            lambda result: self.results.get(result, None),
        )

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


class FileDialog(BaseDialog):
    native_cls = None
    method_name = None
    default_location = PickerLocationId.DocumentsLibrary

    def show(self, host_window, future):
        self._create_native(host_window)

        if self.result is not TEST_RESULT_UNSET:
            if self.pre_close_test_method:
                self.pre_close_test_method(self.interface)
            future.set_result(self.result)
            return

        self._set_future_result_from_async_operation(
            getattr(self.native, self.method_name)(),
            future,
            self.convert_result,
        )

    def _create_native(self, host_window):
        self.native = self.native_cls(self._window_id(host_window))
        self.native.SuggestedStartLocation = self._location_from_path(
            self.initial_directory
        )
        if hasattr(self.native, "ViewMode"):
            self.native.ViewMode = PickerViewMode.List
        return self.native

    def _file_type(self, file_type):
        return file_type if file_type.startswith(".") else f".{file_type}"

    def _location_from_path(self, path):
        if path is None:
            return self.default_location

        path = Path(path)
        home = Path.home()
        known_locations = {
            home / "Desktop": PickerLocationId.Desktop,
            home / "Documents": PickerLocationId.DocumentsLibrary,
            home / "Downloads": PickerLocationId.Downloads,
            home / "Music": PickerLocationId.MusicLibrary,
            home / "Pictures": PickerLocationId.PicturesLibrary,
            home / "Videos": PickerLocationId.VideosLibrary,
        }

        for known_path, location in known_locations.items():
            try:
                if path.resolve() == known_path.resolve():
                    return location
            except OSError:
                pass

        return self.default_location

    def _path_from_result(self, result):
        if not result:
            return None

        path = result.Path
        return Path(path) if path else None

    def _path_exists(self, path):
        try:
            return Path(path).exists()
        except OSError:
            return False


class SaveFileDialog(FileDialog):
    native_cls = FileSavePicker
    method_name = "PickSaveFileAsync"

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

    def _create_native(self, host_window):
        native = super()._create_native(host_window)
        native.SuggestedFileName = self.filename or ""
        if self.initial_directory is not None and self._path_exists(
            self.initial_directory
        ):
            try:
                native.SuggestedFolder = str(self.initial_directory)
            except ComError:
                pass

        if self.file_types:
            file_type_choices = native.FileTypeChoices
            if len(self.file_types) > 1:
                file_type_choices.Insert(
                    "All matching files",
                    [self._file_type(file_type) for file_type in self.file_types],
                )

            for file_type in self.file_types:
                extension = self._file_type(file_type)
                file_type_choices.Insert(f"{file_type.upper()} files", [extension])

            native.DefaultFileExtension = self._file_type(self.file_types[0])

        return native

    def convert_result(self, result):
        return self._path_from_result(result)


class OpenFileDialog(FileDialog):
    native_cls = FileOpenPicker

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

        self.method_name = (
            "PickMultipleFilesAsync" if multiple_select else "PickSingleFileAsync"
        )

    def _create_native(self, host_window):
        native = super()._create_native(host_window)
        if self.file_types:
            for file_type in self.file_types:
                native.FileTypeFilter.Append(self._file_type(file_type))
        return native

    def convert_result(self, result):
        if self.multiple_select:
            paths = [self._path_from_result(item) for item in result or []]
            paths = [path for path in paths if path is not None]
            return paths or None

        return self._path_from_result(result)


class SelectFolderDialog(FileDialog):
    native_cls = FolderPicker
    method_name = "PickSingleFolderAsync"

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

    def convert_result(self, result):
        path = self._path_from_result(result)
        if path is None:
            return None
        return [path] if self.multiple_select else path
