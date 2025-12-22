from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import window as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_to_main_window(gv_tool.Window, tool.MainWindowWidget,tool.Project)
    core.connect_signals(gv_tool.Window)

def deactivate():
    core.remove_main_menu_actions(gv_tool.Window,tool.MainWindowWidget)


def retranslate_ui():
    core.retranslate_ui(gv_tool.Window, tool.MainWindowWidget)


def on_new_project():
    pass


def create_widget(data: object, parent: QWidget):
    core.create_widget(data,parent, gv_tool.Window,gv_tool.SceneView)

def widget_created(widget: ui.GraphWidget):
    core.register_widget(widget, gv_tool.Window)
    core.connect_widget(widget, gv_tool.Window,tool.Util)