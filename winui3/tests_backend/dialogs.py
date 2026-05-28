class DialogsMixin:
    supports_multiple_select_folder = True

    def setup_info_dialog_result(self, dialog, pre_close_test_method=None):
        if pre_close_test_method:
            pre_close_test_method(dialog)
        dialog._impl.result = None

    def setup_question_dialog_result(self, dialog, result):
        dialog._impl.result = result

    def setup_confirm_dialog_result(self, dialog, result):
        dialog._impl.result = result

    def setup_error_dialog_result(self, dialog):
        dialog._impl.result = None

    def setup_stack_trace_dialog_result(self, dialog, result):
        dialog._impl.result = result

    def setup_save_file_dialog_result(self, dialog, result):
        dialog._impl.result = result

    def setup_open_file_dialog_result(self, dialog, result, multiple_select):
        dialog._impl.result = result

    def setup_select_folder_dialog_result(self, dialog, result, multiple_select):
        dialog._impl.result = result

    def is_modal_dialog(self, dialog):
        return True
