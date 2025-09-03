from bsdd_gui import tool
from bsdd_gui.core import console_widget as core


def connect():
    core.create_console_trigger(tool.MainWindowWidget, tool.ConsoleWidget)


def on_new_project():
    pass


def retranslate_ui():
    pass


def close_console():
    core.close(tool.ConsoleWidget)
