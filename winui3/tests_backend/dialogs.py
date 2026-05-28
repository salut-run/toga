import asyncio

from win32more.Microsoft.Windows.Storage.Pickers import (
    FileOpenPicker,
    FileSavePicker,
    FolderPicker,
    PickerLocationId,
    PickerViewMode,
)
from win32more.Windows.Foundation import AsyncStatus

import toga


class FakePickerOperation:
    def __init__(self, result=None, exception=None):
        self.result = result
        self.exception = exception
        self.Completed = None

    def GetResults(self):
        if self.exception:
            raise self.exception
        return self.result

    def complete(self, async_status):
        self.Completed(self, async_status)


class DialogsMixin:
    supports_multiple_select_folder = False

    def setup_dialog_result(self, dialog, result, pre_close_test_method=None):
        dialog._impl.interface = dialog
        dialog._impl.result = result
        dialog._impl.pre_close_test_method = pre_close_test_method

    def setup_info_dialog_result(self, dialog, pre_close_test_method=None):
        self.setup_dialog_result(dialog, None, pre_close_test_method)

    def setup_question_dialog_result(self, dialog, result):
        self.setup_dialog_result(dialog, result)

    def setup_confirm_dialog_result(self, dialog, result):
        self.setup_dialog_result(dialog, result)

    def setup_error_dialog_result(self, dialog):
        self.setup_dialog_result(dialog, None)

    def setup_stack_trace_dialog_result(self, dialog, result):
        self.setup_dialog_result(dialog, result)

    def _file_type(self, file_type):
        return file_type if file_type.startswith(".") else f".{file_type}"

    def _vector_values(self, vector):
        return [vector.GetAt(index) for index in range(len(vector))]

    def _expected_location(self, dialog):
        initial_directory = dialog._impl.initial_directory
        if initial_directory is None:
            return PickerLocationId.DocumentsLibrary

        return dialog._impl._location_from_path(initial_directory)

    def _assert_save_file_dialog_native(self, dialog):
        native = dialog._impl.native
        assert isinstance(native, FileSavePicker)
        assert native.SuggestedFileName == dialog._impl.filename
        assert native.SuggestedStartLocation == self._expected_location(dialog)

        if dialog._impl.file_types:
            assert native.DefaultFileExtension == self._file_type(
                dialog._impl.file_types[0]
            )

            expected_choices = {}
            if len(dialog._impl.file_types) > 1:
                expected_choices["All matching files"] = [
                    self._file_type(file_type) for file_type in dialog._impl.file_types
                ]

            for file_type in dialog._impl.file_types:
                extension = self._file_type(file_type)
                expected_choices[f"{file_type.upper()} files"] = [extension]

            assert native.FileTypeChoices.Size == len(expected_choices)
            for label, extensions in expected_choices.items():
                assert (
                    self._vector_values(native.FileTypeChoices.Lookup(label))
                    == extensions
                )
        else:
            assert native.DefaultFileExtension == ""
            assert native.FileTypeChoices.Size == 0

    def setup_save_file_dialog_result(self, dialog, result):
        self.setup_dialog_result(
            dialog,
            result,
            pre_close_test_method=self._assert_save_file_dialog_native,
        )

    def _assert_open_file_dialog_native(self, dialog):
        native = dialog._impl.native
        assert isinstance(native, FileOpenPicker)
        assert native.SuggestedStartLocation == self._expected_location(dialog)
        assert native.ViewMode == PickerViewMode.List

        expected_filters = [
            self._file_type(file_type) for file_type in dialog._impl.file_types or []
        ]
        assert self._vector_values(native.FileTypeFilter) == expected_filters

    def setup_open_file_dialog_result(self, dialog, result, multiple_select):
        self.setup_dialog_result(
            dialog,
            result,
            pre_close_test_method=self._assert_open_file_dialog_native,
        )

    def _assert_select_folder_dialog_native(self, dialog):
        native = dialog._impl.native
        assert isinstance(native, FolderPicker)
        assert native.SuggestedStartLocation == self._expected_location(dialog)
        assert native.ViewMode == PickerViewMode.List

    def setup_select_folder_dialog_result(self, dialog, result, multiple_select):
        if result and multiple_select:
            result = result[-1:]
        self.setup_dialog_result(
            dialog,
            result,
            pre_close_test_method=self._assert_select_folder_dialog_native,
        )

    async def assert_picker_operation_completion(self):
        dialog = toga.OpenFileDialog("Open file")

        async def picker_result(operation, async_status):
            future = asyncio.get_running_loop().create_future()
            dialog._impl._set_future_result_from_async_operation(
                operation,
                future,
                lambda result: f"converted {result}",
            )
            operation.complete(async_status)
            return await asyncio.wait_for(future, timeout=1)

        assert (
            await picker_result(FakePickerOperation("path"), AsyncStatus.Completed)
        ) == "converted path"
        assert (
            await picker_result(FakePickerOperation("path"), AsyncStatus.Canceled)
            is None
        )
        assert (
            await picker_result(FakePickerOperation("path"), AsyncStatus.Error) is None
        )
        assert (
            await picker_result(
                FakePickerOperation(exception=OSError("picker failed")),
                AsyncStatus.Completed,
            )
            is None
        )

    def is_modal_dialog(self, dialog):
        return True
