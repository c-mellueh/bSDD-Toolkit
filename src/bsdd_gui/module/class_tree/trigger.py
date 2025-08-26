from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui import tool
from bsdd_gui.core import class_tree as core
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QDropEvent

TOOGLE_CONSOLE_ACTION = "toggle_console"
if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.ClassTree, tool.ClassEditor)
    core.connect_to_main_window(tool.ClassTree, tool.MainWindow, tool.Util)
    core.define_class_tree_context_menu(tool.MainWindow, tool.ClassTree, tool.ClassEditor)


def on_new_project():
    core.reset_views(tool.ClassTree, tool.Project)


def retranslate_ui():
    pass


def close_event(event):
    pass


def class_view_created(class_view: ui.ClassView):
    core.connect_view(class_view, tool.ClassTree, tool.Project, tool.Util)


def reset_class_views():
    core.reset_views(tool.ClassTree, tool.Project)


def copy_selected_class(view: ui.ClassView):
    core.copy_selected_class(view, tool.ClassTree, tool.ClassEditor)


def create_context_menu(view: ui.ClassView, pos):
    core.create_context_menu(view, pos, tool.ClassTree)


def delete_selection(view: ui.ClassView):
    core.delete_selection(view, tool.ClassTree, tool.Popups)
