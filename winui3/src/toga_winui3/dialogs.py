class BaseDialog:
    def __init__(self):
        self.result = None

    def show(self, host_window, future):
        future.set_result(self.result)


class MessageDialog(BaseDialog):
    def __init__(self, title, message):
        super().__init__()
        self.title = title
        self.message = message


class InfoDialog(MessageDialog):
    pass


class QuestionDialog(MessageDialog):
    pass


class ConfirmDialog(MessageDialog):
    pass


class ErrorDialog(MessageDialog):
    pass


class StackTraceDialog(MessageDialog):
    def __init__(self, title, message, content, retry):
        super().__init__(title, message)
        self.content = content
        self.retry = retry


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
