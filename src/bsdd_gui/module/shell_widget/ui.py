from pyqtconsole.console import PythonConsole

from bsdd_gui import tool
from bsdd_gui.resources.icons import get_icon
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

    def input_buffer(self):
        # QTextCursor.selectedText() (used upstream) returns U+2029 for line
        # breaks, which Python's tokenizer rejects. Normalize to '\n'.
        return super().input_buffer().replace("\u2029", "\n")
