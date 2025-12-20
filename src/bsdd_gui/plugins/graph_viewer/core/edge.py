from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtGui import QPainter

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.edge import ui, constants
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants
    from bsdd_gui.plugins.graph_viewer.module.settings import ui as setting_ui


def connect_signals(
    edge: Type[gv_tool.Edge],
    window: Type[gv_tool.Window],
    scene_view: Type[gv_tool.SceneView],
    settings: Type[gv_tool.Settings],
):
    window.signals.active_edgetype_requested.connect(edge.request_active_edge)
    edge.signals.edge_drag_started.connect(scene_view.add_item)
    edge.signals.edge_drag_finished.connect(scene_view.remove_item)
    edge.signals.new_edge_created.connect(scene_view.add_item)

    edge.connect_internal_signals()
    settings.signals.widget_created.connect(lambda sw: add_settings(edge, settings))


def add_settings(edge: Type[gv_tool.Edge], settings: Type[gv_tool.Settings]):
    type_widget = edge.create_edge_type_settings_widget()

    for row in edge.create_edge_toggles():
        type_widget._root.addLayout(row)

    routing_widget = edge.create_edge_routing_settings_widget()
    edge.connect_settings_widgets(type_widget, routing_widget)
    settings.add_content_widget(routing_widget)
    settings.add_content_widget(type_widget)


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


def paint_edge_legend(edge_legend: ui._EdgeLegendIcon, edge: Type[gv_tool.Edge]):
    p = QPainter(edge_legend)
    p.setRenderHint(QPainter.Antialiasing, True)
    rect = edge_legend.rect()
    y = rect.center().y()
    x1 = rect.left() + 2
    x2 = rect.right() - 2
    p.setPen(edge.create_pen_for_edgestyle())
    p.drawLine(int(x1), int(y), int(x2), int(y))
