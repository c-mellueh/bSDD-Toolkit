from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import buchheim as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_signals(gv_tool.Buchheim, gv_tool.SceneView)


def deactivate():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_tree():
    core.create_tree(
        gv_tool.Buchheim,
        gv_tool.Window,
        gv_tool.Edge,
        gv_tool.Node,
        gv_tool.SceneView,
        gv_tool.Physics,
    )
