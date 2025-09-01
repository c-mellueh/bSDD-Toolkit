from PySide6.QtWidgets import QDialog

from bsdd_gui.module.search import trigger
from bsdd_gui.resources.icons import get_icon
from .qt import ui_Widget


class SearchDialog(QDialog, ui_Widget.Ui_Search):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(get_icon())
        self.search_mode = None
        self.return_value = None
        self.tableWidget.itemDoubleClicked.connect(lambda _: trigger.item_double_clicked(self))

    def paintEvent(self, event):
        super().paintEvent(event)
        trigger.refresh_window(self)
