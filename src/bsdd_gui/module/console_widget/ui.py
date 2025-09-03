from pyqtconsole.console import PythonConsole

from bsdd_gui import tool
from bsdd_gui.resources.icons import get_icon
from . import trigger


class Console(PythonConsole):
    def __init__(self, *args, **kwds):
        super(Console, self).__init__(*args, **kwds)
        self.setWindowIcon(get_icon())
        self.setWindowTitle(tool.Util.get_window_title("Console"))

    def closeEvent(self, event):
        trigger.close_console()
        super().closeEvent(event)
