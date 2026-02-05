from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import group_of_properties as core
from bsdd_gui.core import class_property_table_view as ptv_core
from bsdd_gui.core import class_tree_view as ctv_core

from typing import TYPE_CHECKING,Type

if TYPE_CHECKING:
    from .views import GopClassView, GopPropertyView
    from PySide6.QtCore import QPoint


def connect():
    core.connect_to_main_window(
        tool.GroupOfProperties, tool.MainWindowWidget, tool.Project, tool.ClassEditorWidget
    )
    core.connect_signals(
        tool.GroupOfProperties,
        tool.GopClassView,
        tool.GopPropertyView,
        tool.ClassEditorWidget,
        tool.ClassPropertyEditorWidget,
        tool.Project,
    )


def retranslate_ui():
    core.retranslate_ui(tool.GroupOfProperties, tool.MainWindowWidget)


def on_new_project():
    core.reset_models(tool.GopClassView, tool.Project, tool.MainWindowWidget)


def create_widget(data: object, parent):
    core.create_widget(data, parent, tool.GroupOfProperties)


def widget_created(widget):
    core.register_widget(widget, tool.GroupOfProperties)
    core.connect_widget(widget, tool.GroupOfProperties, tool.GopClassView,tool.GopPropertyView, tool.ClassEditorWidget)


# CLassTreeView


def class_view_created(view: GopClassView):
    core.register_class_view(view, tool.GopClassView)
    core.add_columns_to_class_view(view, tool.GopClassView, tool.Project)
    ctv_core.add_context_menu_to_view(view, tool.GopClassView, tool.ClassEditorWidget)
    core.connect_class_view(view, tool.GopClassView)


def context_menu_requested(view: GopClassView, pos: QPoint):
    from .views import GopClassView, GopPropertyView
    if isinstance(view,GopClassView):
        core.create_context_menu(view, pos, tool.GopClassView)
    else:
        core.create_context_menu(view, pos, tool.GopPropertyView)


### PropertyTable View


def property_view_created(view: GopPropertyView):
    core.register_property_view(view, tool.GopPropertyView)
    ptv_core.add_columns_to_view(view, tool.GopPropertyView, tool.Project)
    ptv_core.add_context_menu_to_view(view, tool.GopPropertyView)
    core.connect_property_view(view, tool.GopPropertyView)

def copy_selected(
    view: GopPropertyView, view_tool: Type[ tool.GopPropertyView]
):
    ptv_core.copy_property_to_clipboard(view, view_tool)


def paste_clipboard(
    view: GopPropertyView, view_tool: Type[tool.GopPropertyView]
):
    core.paste_property_from_clipboard(
        view, view_tool, tool.PropertyTableWidget, tool.Project, tool.Util,tool.GroupOfProperties
    )