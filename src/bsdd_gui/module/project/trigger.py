from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import project as core
from typing import TYPE_CHECKING


def connect():
    core.create_main_menu_actions(tool.Project, tool.MainWindowWidget)
    core.connect_signals(tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.Project, tool.MainWindowWidget)


def on_new_project():
    pass


def new_clicked():
    core.new_file_clicked(
        tool.Project, tool.DictionaryEditorWidget, tool.Popups, tool.MainWindowWidget
    )
    pass


def open_clicked():
    core.open_file_clicked(
        tool.Project, tool.Appdata, tool.MainWindowWidget, tool.Popups, tool.Plugins
    )
    pass


def add_clicked():
    # TODO
    pass


def save_clicked():
    core.save_clicked(tool.Project, tool.Popups, tool.Appdata, tool.MainWindowWidget)
    pass


def save_as_clicked():
    core.save_as_clicked(tool.Project, tool.Popups, tool.Appdata, tool.MainWindowWidget)
    pass
