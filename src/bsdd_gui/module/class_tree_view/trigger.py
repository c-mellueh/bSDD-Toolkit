from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui import tool
from bsdd_gui.core import class_tree_view as core
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QDropEvent

TOOGLE_CONSOLE_ACTION = "toggle_console"
if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.ClassTree, tool.Project)
    core.connect_to_main_window(tool.ClassTree, tool.MainWindow, tool.Util)


def on_new_project():
    core.reset_models(tool.ClassTree, tool.Project, tool.MainWindow)


def retranslate_ui():
    pass


def close_event(event):
    pass


def class_view_created(view: ui.ClassView):
    core.register_view(view, tool.ClassTree)
    core.add_columns_to_view(view, tool.ClassTree, tool.Project, tool.Util)
    core.add_context_menu_to_view(view, tool.ClassTree, tool.ClassEditor)
    core.connect_view(view, tool.ClassTree)


def copy_selected_class(view: ui.ClassView):
    core.copy_selected_class(view, tool.ClassTree, tool.ClassEditor)


def context_menu_requested(view: ui.ClassView, pos):
    core.create_context_menu(view, pos, tool.ClassTree)


def delete_selection(view: ui.ClassView):
    core.delete_selection(view, tool.ClassTree, tool.Popups, tool.Project)


def group_selection(view: ui.ClassView):
    core.group_selection(view, tool.ClassTree, tool.ClassEditor)


def search_class(view: ui.ClassView):
    core.search_class(view, tool.Search, tool.ClassTree, tool.Project)
