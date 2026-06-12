from bsdd_gui import tool
from bsdd_gui.core import main_window_widget as core

TOOGLE_CONSOLE_ACTION = "toggle_console"


def connect():
    core.connect_main_window(tool.MainWindowWidget, tool.ClassTreeView, tool.PropertySetTableView)


def on_new_project():
    core.refresh_status_bar(tool.MainWindowWidget, tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.MainWindowWidget)


def close_event(event):
    core.close_event(
        event, tool.FileLock, tool.Project, tool.Util, tool.Popups, tool.MainWindowWidget
    )


def refresh_status_bar():
    core.refresh_status_bar(tool.MainWindowWidget, tool.Project)


def toggle_console():
    core.toggle_console(tool.MainWindowWidget)
    core.retranslate_ui(tool.MainWindowWidget)


def update_pset_combobox():
    core.update_pset_combobox(tool.MainWindowWidget, tool.Project, tool.PropertySetTableView)
