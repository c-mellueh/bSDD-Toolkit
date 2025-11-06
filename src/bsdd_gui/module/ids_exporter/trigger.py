from __future__ import annotations
from PySide6.QtCore import QPoint
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import ids_exporter as core
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import IdsWidget
    from . import model_views

def connect():
    core.connect_to_main_window(tool.IdsExporter,tool.MainWindowWidget,tool.Project)
    core.connect_signals(tool.IdsExporter,tool.IdsClassView)

def retranslate_ui():
    core.retranslate_ui(tool.GraphViewWidget, tool.MainWindowWidget)

def on_new_project():
    pass


def create_widget(data: object, parent: IdsWidget):
    core.create_widget(data, parent, tool.IdsExporter)


def create_dialog(data: object, parent: IdsWidget):
    core.create_dialog(data, parent, tool.IdsExporter)


def widget_created(widget: IdsWidget):
    core.register_widget(widget, tool.IdsExporter)
    core.register_fields(widget, tool.IdsExporter)
    core.register_validators(widget, tool.IdsExporter, tool.Util)
    core.connect_widget(widget, tool.IdsExporter,tool.IdsClassView)


def class_view_created(view: model_views.ClassView):
    core.register_view(view, tool.IdsClassView)
    core.add_columns_to_view(view, tool.IdsClassView,tool.IdsExporter)
    #core.add_context_menu_to_view(view, tool.IdsClassView, tool.ClassEditorWidget)
    core.connect_view(view, tool.IdsClassView)

def context_menu_requested(view: model_views.ClassView, pos: QPoint):
    pass
    #TODO: add COntext menu handling
    #core.create_context_menu(view, pos, tool.ItemViewTool)