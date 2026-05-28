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

    def setup_save_file_dialog_result(self, dialog, result):
        self.setup_dialog_result(dialog, result)

    def setup_open_file_dialog_result(self, dialog, result, multiple_select):
        self.setup_dialog_result(dialog, result)

    def setup_select_folder_dialog_result(self, dialog, result, multiple_select):
        if result and multiple_select:
            result = result[-1:]
        self.setup_dialog_result(dialog, result)

    def is_modal_dialog(self, dialog):
        return True
