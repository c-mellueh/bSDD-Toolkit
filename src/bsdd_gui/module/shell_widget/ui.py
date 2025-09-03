from pyqtconsole.console import PythonConsole

from bsdd_gui import tool
from bsdd_gui.resources.icons import get_icon
from . import trigger
from PySide6.QtCore import Signal


class Shell(PythonConsole):
    closed = Signal()
    opened = Signal()

    def __init__(self, *args, **kwds):
        super(Shell, self).__init__(*args, **kwds)
        self.setWindowIcon(get_icon())
        self.setWindowTitle(tool.Util.get_window_title("Console"))

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
