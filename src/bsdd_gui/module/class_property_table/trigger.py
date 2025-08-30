from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_property_table as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.ClassPropertyTable, tool.MainWindow)
    core.connect_signals(
        tool.ClassPropertyTable, tool.MainWindow, tool.PropertySetTable, tool.ClassPropertyEditor
    )


def retranslate_ui():
    pass


def on_new_project():
    pass


def table_view_created(view: ui.ClassPropertyTable):
    core.connect_view(view, tool.ClassPropertyTable, tool.MainWindow)
