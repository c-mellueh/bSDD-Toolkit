from __future__ import annotations
import bsdd_gui
from bsdd_parser import BsddClass
from bsdd_gui import tool
from bsdd_gui.core import property_set_table_view as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.PropertySetTable)
    core.connect_to_main_window(tool.PropertySetTable, tool.MainWindow)
    core.define_context_menu(tool.MainWindow, tool.PropertySetTable)


def retranslate_ui():
    core.retranslate_ui(tool.PropertySetTable)
    pass


def on_new_project():
    core.reset_models(tool.PropertySetTable, tool.Project, tool.MainWindow)


def view_created(view: ui.PsetTableView):
    core.register_view(view, tool.PropertySetTable)
    core.add_columns_to_view(view, tool.PropertySetTable, tool.Project, tool.MainWindow, tool.Util)
    core.add_context_menu_to_view(view, tool.PropertySetTable)
    core.connect_view(view, tool.PropertySetTable, tool.Project, tool.MainWindow)


def new_property_set_requested(bsdd_class: BsddClass):
    core.create_new_property_set(bsdd_class, tool.PropertySetTable, tool.Util)


def context_menu_requested(view: ui.PsetTableView, pos):
    core.create_context_menu(view, pos, tool.PropertySetTable)


def delete_selection(view: ui.PsetTableView):
    core.delete_selection(view, tool.PropertySetTable, tool.ClassPropertyTable, tool.MainWindow)
