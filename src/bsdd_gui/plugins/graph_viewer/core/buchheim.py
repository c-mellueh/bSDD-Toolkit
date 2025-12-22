from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, QPointF
from PySide6.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.buchheim import ui


def connect_signals(buchheim: Type[gv_tool.Buchheim], scene_view: Type[gv_tool.SceneView]):
    scene_view.signals.buchheim_requested.connect(buchheim.request_tree_creation)
    buchheim.connect_internal_signals()

def disconnect_signals(buchheim: Type[gv_tool.Buchheim]):
    buchheim.disconnect_internal_signals()
    buchheim.disconnect_external_signals()

def create_tree(
    buchheim: Type[gv_tool.Buchheim],
    window: Type[gv_tool.Window],
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
    scene_view: Type[gv_tool.SceneView],
    physics: Type[gv_tool.Physics],
):

    all_nodes, all_edges = node.get_nodes(), edge.get_edges()
    allowed = buchheim.reset_children_dict(all_nodes, all_edges, edge.get_active_edge())
    if not allowed:
        buchheim.create_information(window.get_widget())
        return
    physics.set_running(False)

    roots = buchheim.find_roots(all_nodes)
    root = roots[0]
    buchheim.intialize(root)
    root_x_pos = [n.pos().x() for n in roots]
    root_y_pos = [n.pos().y() for n in roots]
    root_mid_x = (min(root_x_pos) + max(root_x_pos)) / 2
    root_mid_y = (min(root_y_pos) + max(root_y_pos)) / 2
    min_x = max(min(n.pos().x() for n in all_nodes), 500.0)
    min_y = max(min(n.pos().y() for n in all_nodes), 500.0)
    center_pos = QPointF(root_mid_x, root_mid_y)
    helper_node = node.add_node(None, center_pos)

    buchheim.get_properties().children_dict[helper_node] = roots
    for r in roots:
        buchheim.get_properties().parent_dict[r] = helper_node

    buchheim.intialize(helper_node)
    buchheim.buchheim(helper_node)
    buchheim.rearrange(helper_node, QPointF(min_x, min_y))
    node.remove_node(helper_node, scene_view.get_scene())
    scene_view.request_center_scene()
