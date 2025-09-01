from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_table as core
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QTreeView

if TYPE_CHECKING:
    from . import ui, views


def connect():
    core.create_main_menu_actions(tool.PropertyTable, tool.MainWindow, tool.PropertyEditor)
    core.connect_signals(tool.PropertyTable, tool.PropertyEditor, tool.MainWindow, tool.ClassTree)


def retranslate_ui():
    core.retranslate_ui(tool.PropertyTable, tool.MainWindow, tool.Util)
    pass


def create_widget(parent_widget):
    core.create_widget(parent_widget, tool.PropertyTable, tool.Util, tool.MainWindow)


def widget_created(widget: ui.PropertyWidget):
    core.register_widget(widget, tool.PropertyTable)


def widget_removed(widget: ui.PropertyWidget):
    core.unregister_widget(widget, tool.PropertyTable)


def search_property(view: QTreeView):
    core.search_property(view, tool.PropertyTable, tool.Search, tool.Project)


def on_new_project():
    pass
