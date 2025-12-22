from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import node as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui
    from PySide6.QtGui import QPainter


def activate():
    core.connect_signals(
        gv_tool.Node, gv_tool.Edge, gv_tool.SceneView, gv_tool.Settings, tool.Project
    )


def deactivate():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def node_double_clicked(node):
    core.node_double_clicked(
        node, tool.PropertyTableWidget, tool.ClassTreeView, tool.MainWindowWidget
    )


def paint_node_legend(node_legend):
    core.paint_node_legend(node_legend, gv_tool.Node)


def paint_node(painter:QPainter,node:ui.Node):
    core.paint_node(node,painter,gv_tool.Node)