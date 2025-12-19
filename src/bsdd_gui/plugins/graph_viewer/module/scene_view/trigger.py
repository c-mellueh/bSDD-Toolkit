from __future__ import annotations
import bsdd_gui
from bsdd_json import BsddClass, BsddProperty

from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import scene_view as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui

    from PySide6.QtCore import QPointF


def activate():
    core.connect_signals(gv_tool.Window, gv_tool.SceneView)


def deactivate():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def delete_selection():
    core.delete_selection(gv_tool.SceneView, tool.Project,gv_tool.Edge,gv_tool.Node)


def resize_event(event):
    return core.resize_event(event, gv_tool.SceneView)


def mouse_press_event(event):
    return core.mouse_press_event(event, gv_tool.SceneView, gv_tool.Node, gv_tool.Edge)


def mouse_release_event(event):
    return core.mouse_release_event(event, gv_tool.SceneView, gv_tool.Node, gv_tool.Edge)


def mouse_move_event(event):
    return core.mouse_move_event(event, gv_tool.SceneView, gv_tool.Edge)


def drag_enter_event(event):
    return core.drag_enter_event(event, gv_tool.SceneView)


def drag_move_event(event):
    return core.drag_move_event(event, gv_tool.SceneView)


def handle_drop_event(event):
    core.drop_event(
        event, gv_tool.SceneView, tool.ClassTreeView, tool.PropertyTableWidget, tool.Project
    )


def insert_classes(classes: list[BsddClass], postion: QPointF):
    core.insert_classes_in_scene(
        classes, postion, gv_tool.SceneView, gv_tool.Node, tool.IfcHelper, tool.Project
    )


def insert_properties(properties: list[BsddProperty], postion: QPointF):
    core.insert_properties_in_scene(
        properties, postion, gv_tool.SceneView, gv_tool.Node, tool.Project
    )


def recalculate_edges():
    core.recalculate_edges(gv_tool.SceneView, gv_tool.Node, gv_tool.Edge, tool.Project)
