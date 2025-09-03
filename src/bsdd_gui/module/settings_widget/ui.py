from PySide6.QtWidgets import QDialog

from bsdd_gui.resources.icons import get_icon


class Dialog(QDialog):
    def __init__(self):
        super().__init__()
        from .qt.ui_Widget import Ui_Settings

        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.setWindowIcon(get_icon())
