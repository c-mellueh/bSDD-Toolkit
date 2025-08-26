from __future__ import annotations
import bsdd_gui
from bsdd_parser import BsddClass
from bsdd_gui import tool
from bsdd_gui.core import property_set_table as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.PropertySetTable, tool.MainWindow)


def retranslate_ui():
    pass


def on_new_project():
    pass


def table_view_created(view: ui.PsetTableView):
    core.connect_view(view, tool.PropertySetTable, tool.Project, tool.MainWindow)


def create_new_property_set(bsdd_class: BsddClass):
    core.create_new_property_set(bsdd_class, tool.PropertySetTable, tool.Util)


def reset_views():
    core.reset_views(tool.PropertySetTable)
