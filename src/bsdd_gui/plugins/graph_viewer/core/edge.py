from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.edge import ui, constants
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants


def connect_signals(
    edge: Type[gv_tool.Edge], window: Type[gv_tool.Window], scene_view: Type[gv_tool.SceneView]
):
    window.signals.active_edgetype_requested.connect(edge.request_active_edge)
    edge.signals.edge_drag_started.connect(scene_view.add_item)
    edge.signals.edge_drag_finished.connect(scene_view.remove_item)
    edge.signals.new_edge_created.connect(scene_view.add_item)

    edge.connect_internal_signals()


def set_active_edge(
    edge_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    scene_view: Type[gv_tool.SceneView],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    edge.set_active_edge(edge_type)
    if edge_type:
        style_sheet = edge.get_edge_stylesheet(edge_type)
    else:
        style_sheet = ""
    view.setStyleSheet(style_sheet)


def create_relation(
    start_node: Node,
    end_node: Node,
    relation_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
):

    if start_node.node_type == node_constants.CLASS_NODE_TYPE:

        if end_node.node_type in [
            node_constants.PROPERTY_NODE_TYPE,
            node_constants.EXTERNAL_PROPERTY_NODE_TYPE,
        ]:
            if relation_type == constants.C_P_REL:
                edge.create_class_property_relation(start_node, end_node, project.get())
        elif end_node.node_type in [
            node_constants.CLASS_NODE_TYPE,
            node_constants.IFC_NODE_TYPE,
            node_constants.EXTERNAL_CLASS_NODE_TYPE,
        ]:
            edge.create_class_class_relation(start_node, end_node, project.get(), relation_type)
    elif start_node.node_type == node_constants.PROPERTY_NODE_TYPE:
        if end_node.node_type == node_constants.CLASS_NODE_TYPE:
            edge.create_class_property_relation(start_node, end_node, project.get())
        elif end_node.node_type in [
            node_constants.PROPERTY_NODE_TYPE,
            node_constants.EXTERNAL_PROPERTY_NODE_TYPE,
        ]:
            edge.create_property_property_relation(
                start_node, end_node, project.get(), relation_type
            )

    scene_view.apply_filters(edge.get_filters(), node.get_filters())
