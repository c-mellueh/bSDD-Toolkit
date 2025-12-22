from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import input_bar as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_signals(gv_tool.InputBar, gv_tool.Window, tool.Project)


def deactivate():
    core.disconnect_signals(gv_tool.InputBar)


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_widget():
    core.create_widget(gv_tool.InputBar)


def widget_created(widget):
    core.register_widget(widget, gv_tool.InputBar, gv_tool.Window)
    core.connect_widget(widget, gv_tool.InputBar)


def add_node():
    core.add_node_by_lineinput(gv_tool.InputBar, gv_tool.SceneView, gv_tool.Node, tool.Project)
