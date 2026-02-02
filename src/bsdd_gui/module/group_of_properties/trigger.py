from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import group_of_properties as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .views import ClassView
    from PySide6.QtCore import QPoint


def connect():
    core.connect_to_main_window(tool.GroupOfProperties, tool.MainWindowWidget, tool.Project,tool.ClassEditorWidget)
    core.connect_signals(tool.GroupOfProperties,tool.GopClassView,tool.ClassEditorWidget,tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.GroupOfProperties, tool.MainWindowWidget)


def on_new_project():
    core.reset_models(tool.GopClassView,tool.Project,tool.MainWindowWidget)


def create_widget(data: object, parent):
    core.create_widget(data, parent, tool.GroupOfProperties)


def widget_created(widget):
    core.register_widget(widget, tool.GroupOfProperties)
    core.connect_widget(widget, tool.GroupOfProperties,tool.ClassEditorWidget)

#CLassTreeView


def context_menu_requested(view: ClassView, pos: QPoint):
    core.create_context_menu(view, pos, tool.GopClassView)


def class_view_created(view: ClassView):
    core.register_view(view, tool.GopClassView)
    core.add_columns_to_view(view, tool.GopClassView,tool.Project)
    core.add_context_menu_to_view(view, tool.GopClassView,tool.ClassEditorWidget)
    core.connect_view(view, tool.GopClassView)
