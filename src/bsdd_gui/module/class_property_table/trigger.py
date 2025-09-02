from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_property_table as core
from typing import TYPE_CHECKING
from PySide6.QtCore import QPoint

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.ClassPropertyTable, tool.ClassPropertyEditor)
    core.connect_to_main_window(tool.ClassPropertyTable, tool.MainWindow)


def retranslate_ui():
    core.rentranslate_ui(tool.ClassPropertyTable)


def on_new_project():
    pass


def context_menu_requested(view: ui.ClassPropertyTable, pos: QPoint):
    core.create_context_menu(view, pos, tool.ClassPropertyTable)


def table_view_created(view: ui.ClassPropertyTable):
    core.connect_view(view, tool.ClassPropertyTable, tool.MainWindow)


def view_created(view: ui.ClassPropertyTable):
    core.register_view(view, tool.ClassPropertyTable)
    core.add_columns_to_view(view, tool.ClassPropertyTable)
    core.add_context_menu_to_view(view, tool.ClassPropertyTable)
    core.connect_view(view, tool.ClassPropertyTable)


def view_closed(view: ui.ClassPropertyTable):
    core.remove_view(view, tool.ClassPropertyTable)
