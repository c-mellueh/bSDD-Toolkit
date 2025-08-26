from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QLabel

from bsdd_gui.resources.icons import get_icon
from .qt.ui_DeleteRequest import Ui_DeleteRequest


class DeleteRequestDialog(QDialog, Ui_DeleteRequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(get_icon())
