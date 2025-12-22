from pyqtconsole.console import PythonConsole

from bsdd_gui import tool
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_gui.presets.ui_presets import BaseWindow
from PySide6.QtCore import Signal, Qt


class Shell(
    PythonConsole,
):
    closed = Signal()
    opened = Signal()
    hidden = Signal()
    shown = Signal()
    resized = Signal()
    entered = Signal()

    def __init__(self, *args, **kwds):
        super(Shell, self).__init__(*args, **kwds)
        self.setWindowIcon(get_icon())
        self.setWindowTitle(tool.Util.get_window_title("Console"))
        self.setWindowFlag(Qt.WindowType.Window)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
