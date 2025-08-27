from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import allowed_values_table as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.AllowedValuesTable, tool.MainWindow)
    core.connect_signals(tool.AllowedValuesTable, tool.MainWindow, tool.PropertySetTable)


def retranslate_ui():
    pass


def on_new_project():
    pass


def table_view_created(view: ui.AllowedValuesTable):
    core.connect_view(view, tool.AllowedValuesTable, tool.MainWindow)
