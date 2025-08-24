from PySide6.QtWidgets import QWidget

from . import trigger
from .qt import ui_PropertySelect, ui_FileSelector, ui_Progressbar


class FileSelector(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui_FileSelector.Ui_Util()
        self.ui.setupUi(self)
        self.request_folder = None
        self.extension = None
        self.name: str | None = None
        self.appdata_text = None
        self.request_save = None
        self.single_request = None
        self.update_appdata = None
        self.ui.pushButton.clicked.connect(lambda: trigger.fileselector_clicked(self))

    def paintEvent(self, event):
        super().paintEvent(event)
        trigger.paint_file_selector(self)


class PropertySelector(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui_PropertySelect.Ui_Util()
        self.ui.setupUi(self)
        trigger.main_property_selector_created(self)


class Progressbar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = ui_Progressbar.Ui_Util()
        self.ui.setupUi(self)
