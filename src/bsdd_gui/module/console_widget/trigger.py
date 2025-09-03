from bsdd_gui import tool
from bsdd_gui.core import console_widget as core


def connect():
    core.connect_signals(tool.ConsoleWidget)
    core.connect_to_main_window(tool.MainWindowWidget, tool.ConsoleWidget)


def retranslate_ui():
    core.retranslate_ui(tool.ConsoleWidget)
    pass


def on_new_project():
    pass


def close_console():
    core.close_widget(tool.ConsoleWidget)
