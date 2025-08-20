from bsdd_gui import tool
from bsdd_gui.core import main_window as core
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QDropEvent

TOOGLE_CONSOLE_ACTION = "toggle_console"


def connect():
    core.connect_main_window(tool.MainWindow,tool.PropertySetList)

def on_new_project():
    pass

def retranslate_ui():
    pass

def close_event(event):
    pass