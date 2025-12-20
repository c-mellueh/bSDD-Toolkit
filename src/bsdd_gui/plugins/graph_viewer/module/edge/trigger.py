from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import edge as core

from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui, constants


def activate():
    core.connect_signals(gv_tool.Edge, gv_tool.Window, gv_tool.SceneView,gv_tool.Settings)


def deactivate():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def set_active_edge(edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
    core.set_active_edge(edge_type, gv_tool.SceneView, gv_tool.Edge)


def create_relation(start_node, end_node, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
    core.create_relation(
        start_node, end_node, edge_type, gv_tool.Edge, gv_tool.Node, gv_tool.SceneView, tool.Project
    )

def paint_edge_legend(edge_legend:ui._EdgeLegendIcon):
    core.paint_edge_legend(edge_legend,gv_tool.Edge)