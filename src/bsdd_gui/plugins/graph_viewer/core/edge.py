from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.edge import ui, constants


def connect_signals(edge: Type[gv_tool.Edge], window: Type[gv_tool.Window]):
    window.signals.active_edgetype_requested.connect(edge.request_active_edge)


def set_active_edge(
    edge_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    scene_view: Type[gv_tool.SceneView],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    edge.set_active_edge(edge_type)
    if  edge_type:
        style_sheet = edge.get_edge_stylesheet(edge_type)
    else:
        style_sheet = ""
    view.setStyleSheet(style_sheet)
