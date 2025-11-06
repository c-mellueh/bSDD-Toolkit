from __future__ import annotations
import bsdd_gui
from bsdd_json import BsddClass
from bsdd_gui import tool
from bsdd_gui.core import property_set_table_view as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.PropertySetTableView)
    core.connect_to_main_window(
        tool.PropertySetTableView, tool.MainWindowWidget, tool.Util, tool.ClassPropertyTableView
    )
    core.define_context_menu(
        tool.MainWindowWidget, tool.PropertySetTableView, tool.Util, tool.ClassPropertyTableView
    )


def retranslate_ui():
    core.retranslate_ui(tool.PropertySetTableView)
    pass


def on_new_project():
    core.reset_models(tool.PropertySetTableView, tool.Project, tool.MainWindowWidget)


def view_created(view: ui.PsetTableView):
    core.register_view(view, tool.PropertySetTableView)
    core.add_columns_to_view(
        view, tool.PropertySetTableView, tool.Project, tool.MainWindowWidget, tool.Util
    )
    core.connect_view(view, tool.PropertySetTableView, tool.Project, tool.MainWindowWidget)


def new_property_set_requested(bsdd_class: BsddClass):
    core.create_new_property_set(bsdd_class, tool.PropertySetTableView, tool.Util)


def context_menu_requested(view: ui.PsetTableView, pos):
    core.create_context_menu(view, pos, tool.PropertySetTableView)


def delete_selection(view: ui.PsetTableView):
    core.delete_selection(
        view, tool.PropertySetTableView, tool.ClassPropertyTableView, tool.MainWindowWidget
    )
