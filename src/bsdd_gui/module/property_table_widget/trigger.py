from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_table_widget as core
from typing import TYPE_CHECKING
from PySide6.QtWidgets import QTreeView

if TYPE_CHECKING:
    from . import ui, views


def connect():
    core.connect_to_main_menu(tool.PropertyTableWidget, tool.MainWindowWidget)
    core.connect_signals(
        tool.PropertyTableWidget,
        tool.PropertyEditorWidget,
        tool.MainWindowWidget,
        tool.ClassTreeView,
        tool.Project,
    )


def retranslate_ui():
    core.retranslate_ui(tool.PropertyTableWidget, tool.MainWindowWidget, tool.Util)


def on_new_project():
    pass


def create_widget():
    core.create_widget(tool.PropertyTableWidget, tool.Util, tool.MainWindowWidget)


def widget_created(widget: ui.PropertyWidget):

    view = widget.tv_properties
    core.register_view(view, tool.PropertyTableWidget)
    core.add_columns_to_view(view, tool.PropertyTableWidget)
    core.add_context_menu_to_view(view, tool.PropertyTableWidget)
    core.connect_view(view, tool.PropertyTableWidget, tool.Util)

    view = widget.tv_classes
    core.register_view(view, tool.PropertyTableWidget)
    core.add_columns_to_view(view, tool.PropertyTableWidget)
    core.add_context_menu_to_view(view, tool.PropertyTableWidget)
    core.connect_view(view, tool.PropertyTableWidget, tool.Util)

    core.register_widget(widget, tool.PropertyTableWidget)
    core.connect_widget(widget, tool.PropertyTableWidget)


### Module Specific Triggers
def search_requested(view: QTreeView):
    core.search_property(view, tool.PropertyTableWidget, tool.SearchWidget, tool.Project)


def context_menu_requested(view: views.PropertyTable | views.ClassTable, pos):
    core.create_context_menu(view, pos, tool.PropertyTableWidget)
