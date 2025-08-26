from PySide6.QtWidgets import QApplication, QMainWindow

from bsdd_gui.resources.icons import get_icon
from . import trigger
from .qt import ui_MainWindow


class MainWindow(QMainWindow, ui_MainWindow.Ui_MainWindow):
    def __init__(self, application: QApplication):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.app: QApplication = application
        self.setWindowIcon(get_icon())
        self.splitter.setOpaqueResize(False)

    # Open / Close windows
    def closeEvent(self, event):
        result = trigger.close_event(event)

    def paintEvent(self, event):
        super().paintEvent(event)
