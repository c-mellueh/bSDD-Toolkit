from __future__ import annotations

from bsdd_gui import tool
from bsdd_gui.core import settings as core


def connect():
    core.create_main_menu_actions(tool.Settings, tool.MainWindow)


def open_window():
    core.open_window(tool.Settings)


def on_new_project():
    pass


def retranslate_ui():
    core.retranslate_ui(tool.Settings, tool.Util)
