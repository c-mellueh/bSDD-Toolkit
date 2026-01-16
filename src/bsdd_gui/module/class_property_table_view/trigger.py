from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_property_table_view as core
from typing import TYPE_CHECKING
from PySide6.QtCore import QPoint

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(
        tool.ClassPropertyTableView,
        tool.ClassPropertyEditorWidget,
        tool.MainWindowWidget,
        tool.Project,
    )
    core.connect_to_main_window(tool.ClassPropertyTableView, tool.MainWindowWidget)


def retranslate_ui():
    core.rentranslate_ui(tool.ClassPropertyTableView)


def on_new_project():
    core.reset_models(tool.ClassPropertyTableView, tool.Project, tool.MainWindowWidget)


def context_menu_requested(view: ui.ClassPropertyTable, pos: QPoint):
    core.create_context_menu(view, pos, tool.ClassPropertyTableView)


def view_created(view: ui.ClassPropertyTable):
    core.register_view(view, tool.ClassPropertyTableView)
    core.add_columns_to_view(view, tool.ClassPropertyTableView, tool.Project)
    core.add_context_menu_to_view(view, tool.ClassPropertyTableView)
    core.connect_view(view, tool.ClassPropertyTableView, tool.Util)


def copy_selected(view: ui.ClassPropertyTable):
    core.copy_property_to_clipboard(view, tool.ClassPropertyTableView)


def paste_clipboard(view: ui.ClassPropertyTable):
    core.paste_property_from_clipboard(
        view, tool.ClassPropertyTableView, tool.PropertyTableWidget, tool.Project, tool.Util
    )
