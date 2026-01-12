from bsdd_gui import tool
from bsdd_gui.core import shell_widget as core


def connect():
    core.connect_signals(tool.ShellWidget)
    core.connect_to_main_window(tool.MainWindowWidget, tool.ShellWidget)


def retranslate_ui():
    core.retranslate_ui(tool.ShellWidget, tool.MainWindowWidget)
    pass


def on_new_project():
    pass


def create_widget():
    core.create_widget(tool.ShellWidget, tool.MainWindowWidget)


def close_widget():
    core.close_widget(tool.ShellWidget)
