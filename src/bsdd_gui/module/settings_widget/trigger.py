from __future__ import annotations

from bsdd_gui import tool
from bsdd_gui.core import settings_widget as core


def connect():
    core.create_main_menu_actions(tool.SettingsWidget, tool.MainWindowWidget)


def open_window():
    core.open_window(tool.SettingsWidget)


def on_new_project():
    pass


def retranslate_ui():
    core.retranslate_ui(tool.SettingsWidget, tool.Util)
