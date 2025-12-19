from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import scene_view as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_signals(gv_tool.Window, gv_tool.SceneView, gv_tool.Edge)


def deactivate():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def delete_selection():
    core.delete_selection(gv_tool.SceneView, tool.Project)


def resize_event(event):
    core.resize_event(event, gv_tool.SceneView)


def mouse_press_event(event):
    core.mouse_press_event(event, gv_tool.SceneView, gv_tool.Node, gv_tool.Edge)


def mouse_release_event(event):
    core.mouse_release_event(event, gv_tool.SceneView, gv_tool.Node, gv_tool.Edge)


def mouse_move_event(event):
    core.mouse_move_event(event, gv_tool.SceneView, gv_tool.Edge)
