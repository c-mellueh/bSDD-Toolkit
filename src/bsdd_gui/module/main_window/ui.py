from PySide6.QtWidgets import QApplication, QMainWindow

from bsdd_gui.resources.icons import get_icon
from . import trigger
from .qt import ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self, application: QApplication):
        super(MainWindow, self).__init__()
        self.ui = ui_MainWindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.app: QApplication = application
        self.setWindowIcon(get_icon())

    # Open / Close windows
    def closeEvent(self, event):
        result = trigger.close_event(event)

    def paintEvent(self, event):
        super().paintEvent(event)
