from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_table_widget as core
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QTreeView

if TYPE_CHECKING:
    from . import ui, views


def connect():
    core.connect_to_main_menu(tool.PropertyTable, tool.MainWindow)
    core.connect_signals(
        tool.PropertyTable, tool.PropertyEditor, tool.MainWindow, tool.ClassTree, tool.Project
    )


def retranslate_ui():
    core.retranslate_ui(tool.PropertyTable, tool.MainWindow, tool.Util)
    pass


def create_widget(parent_widget):
    core.create_widget(parent_widget, tool.PropertyTable, tool.Util, tool.MainWindow)


def widget_created(widget: ui.PropertyWidget):

    view = widget.tv_properties
    core.register_view(view, tool.PropertyTable)
    core.add_columns_to_view(view, tool.PropertyTable)
    core.add_context_menu_to_view(view, tool.PropertyTable)
    core.connect_view(view, tool.PropertyTable, tool.Util)

    view = widget.tv_classes
    core.register_view(view, tool.PropertyTable)
    core.add_columns_to_view(view, tool.PropertyTable)
    core.add_context_menu_to_view(view, tool.PropertyTable)
    core.connect_view(view, tool.PropertyTable, tool.Util)

    core.register_widget(widget, tool.PropertyTable)


def widget_removed(widget: ui.PropertyWidget):
    core.unregister_widget(widget, tool.PropertyTable)
    core.remove_view(widget.tv_properties, tool.PropertyTable)
    core.remove_view(widget.tv_classes, tool.PropertyTable)


def search_requested(view: QTreeView):
    core.search_property(view, tool.PropertyTable, tool.Search, tool.Project)


def context_menu_requested(view: views.PropertyTable | views.ClassTable, pos):
    core.create_context_menu(view, pos, tool.PropertyTable)


def delete_selection(view: QTreeView):
    core.delete_selection(view, tool.PropertyTable, tool.Project)


def on_new_project():
    pass
