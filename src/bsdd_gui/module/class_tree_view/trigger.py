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
    core.connect_signals(tool.ClassTreeView, tool.Project,tool.ClassEditorWidget)
    core.connect_to_main_window(tool.ClassTreeView, tool.MainWindowWidget, tool.Util)


def on_new_project():
    core.reset_models(tool.ClassTreeView, tool.Project, tool.MainWindowWidget)


def retranslate_ui():
    pass


def close_event(event):
    pass


def class_view_created(view: ui.ClassView):
    core.register_view(view, tool.ClassTreeView)
    core.add_columns_to_view(view, tool.ClassTreeView, tool.Project, tool.Util)
    core.add_context_menu_to_view(view, tool.ClassTreeView, tool.ClassEditorWidget)
    core.connect_view(view, tool.ClassTreeView)


def copy_selected_class(view: ui.ClassView):
    core.copy_selected_class(view, tool.ClassTreeView, tool.ClassEditorWidget)


def context_menu_requested(view: ui.ClassView, pos):
    core.create_context_menu(view, pos, tool.ClassTreeView)


def delete_selection(view: ui.ClassView):
    core.delete_selection(view, tool.ClassTreeView, tool.Popups, tool.Project)


def group_selection(view: ui.ClassView):
    core.group_selection(view, tool.ClassTreeView, tool.ClassEditorWidget)


def search_class(view: ui.ClassView):
    core.search_class(view, tool.SearchWidget, tool.ClassTreeView, tool.Project)
