from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import project as core
from typing import TYPE_CHECKING


def connect():
    core.create_main_menu_actions(tool.Project, tool.MainWindow)


def retranslate_ui():
    core.retranslate_ui(tool.Project, tool.MainWindow)


def on_new_project():
    pass


def new_clicked():
    core.new_file_clicked(tool.Project, tool.DictionaryEditor)
    pass


def open_clicked():
    # TODO
    pass


def add_clicked():
    # TODO
    pass


def save_clicked():
    # TODO
    pass


def save_as_clicked():
    # TODO
    pass
