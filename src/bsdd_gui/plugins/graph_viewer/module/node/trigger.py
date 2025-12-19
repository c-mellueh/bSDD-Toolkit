from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import node as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool
if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_signals(gv_tool.Node,gv_tool.Edge,tool.Project)

    
def deactivate():
    pass

    
def retranslate_ui():
    pass

    
def on_new_project():
    pass
