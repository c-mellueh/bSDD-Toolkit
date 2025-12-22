from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtGui import QPainter, QPainterPath, QBrush, QPen
from PySide6.QtCore import Qt, QPointF, QCoreApplication
from bsdd_json import BsddClass, BsddClassRelation, BsddPropertyRelation

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.edge import ui, constants
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node


def connect_signals(
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
    window: Type[gv_tool.Window],
    scene_view: Type[gv_tool.SceneView],
    settings: Type[gv_tool.Settings],
    relationship_editor: Type[tool.RelationshipEditorWidget],
    class_property_table: Type[tool.ClassPropertyTableView],
    property_set_table: Type[tool.PropertySetTableView],
    project: Type[tool.Project],
):

    window.signals.active_edgetype_requested.connect(edge.request_active_edge)
    edge.signals.edge_drag_started.connect(scene_view.add_item)
    edge.signals.edge_drag_finished.connect(scene_view.remove_item)
    edge.signals.new_edge_created.connect(scene_view.add_item)

    edge.connect_internal_signals()
    settings.signals.widget_created.connect(lambda sw: add_settings(edge, settings))
    edge.signals.filter_changed.connect(
        lambda k, v: scene_view.apply_filters(edge.get_filters(), node.get_filters())
    )
    scene_view.signals.clear_scene_requested.connect(lambda: clear_all_edges(edge, scene_view))

    # Connect Outside Signals

    def _handle_rel_update(edge: ui.Edge):
        start_data = edge.start_node.bsdd_data
        widget = relationship_editor.get_widget(start_data)
        if not widget:
            return
        relationship_editor.reset_view(widget.tv_relations)

    def _handle_prop_update(*args, **kwargs):
        class_property_table.reset_views()
        property_set_table.reset_views()

    edge.signals.new_edge_created.connect(_handle_rel_update)
    edge.signals.edge_removed.connect(_handle_rel_update)
    edge.signals.new_class_property_created.connect(_handle_prop_update)
    edge.signals.class_property_removed.connect(_handle_prop_update)


def connect_to_project_signals(
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
):

    # In
    def handle_relation_remove(relation: BsddClassRelation | BsddPropertyRelation):
        active_edge = edge.get_edge_from_relation(relation, project.get())
        if active_edge is None:
            return
        edge.remove_edge(
            active_edge,
            scene_view.get_scene(),
            project.get(),
            only_visual=True,
            allow_parent_deletion=True,
        )

    def handle_relation_add(relation: BsddClassRelation | BsddPropertyRelation):
        start_data, end_data, relation_type = edge.read_relation(relation, project.get())
        start_node = node.get_node_from_bsdd_data(start_data)
        end_node = node.get_node_from_bsdd_data(end_data)
        if not (start_node and end_node):
            return
        active_edge = edge.create_edge(start_node, end_node, edge_type=relation_type)
        edge.add_edge(active_edge)

    def handle_ifc_relation_add(bsdd_class: BsddClass, ifc_code: str):
        start_node = node.get_node_from_bsdd_data(bsdd_class)
        end_node = node.get_node_from_ifc_code(ifc_code)
        if not start_node:
            return
        if not end_node:
            end_node = node.add_ifc_node(ifc_code, start_node.pos() + QPointF(10.0, 10.0))
        if not (start_node and end_node):
            return
        active_edge = edge.create_edge(start_node, end_node, edge_type=constants.IFC_REFERENCE_REL)
        edge.add_edge(active_edge)

    def handle_ifc_relation_remove(bsdd_class: BsddClass, ifc_code: str):
        start_node = node.get_node_from_bsdd_data(bsdd_class)
        if not start_node:
            return
        end_node = node.get_node_from_ifc_code(ifc_code)
        relation = edge.get_edge_from_nodes(start_node, end_node, constants.IFC_REFERENCE_REL)
        if relation is None:
            return
        edge.remove_edge(
            relation,
            scene_view.get_scene(),
            project.get(),
            only_visual=True,
            allow_parent_deletion=True,
        )
        if not edge.get_connected_edges(end_node):
            node.remove_node(end_node, scene_view.get_scene())

    project.signals.class_relation_added.connect(handle_relation_add)
    project.signals.class_relation_removed.connect(handle_relation_remove)
    project.signals.property_relation_added.connect(handle_relation_add)
    project.signals.property_relation_removed.connect(handle_relation_remove)
    project.signals.ifc_relation_addded.connect(handle_ifc_relation_add)
    project.signals.ifc_relation_removed.connect(handle_ifc_relation_remove)

    # Out

    def handle_edge_add(active_edge: ui.Edge):
        relation = edge.get_relation_from_edge(active_edge, project.get())
        if isinstance(relation, BsddClassRelation):
            project.signals.class_relation_added.emit(relation)
        if isinstance(relation, BsddPropertyRelation):
            project.signals.property_relation_added.emit(relation)

    edge.signals.class_relation_removed.connect(project.signals.class_relation_removed.emit)
    edge.signals.property_relation_removed.connect(project.signals.property_relation_removed.emit)
    edge.signals.ifc_reference_added.connect(project.signals.ifc_relation_addded.emit)
    edge.signals.ifc_reference_removed.connect(project.signals.ifc_relation_removed.emit)
    edge.signals.new_edge_created.connect(handle_edge_add)


def clear_all_edges(edge: Type[gv_tool.Edge], scene_view: Type[gv_tool.SceneView]):
    scene = scene_view.get_scene()
    for n in edge.get_edges():
        scene.removeItem(n)
    edge.clear()


def add_settings(edge: Type[gv_tool.Edge], settings: Type[gv_tool.Settings]):
    type_widget = edge.create_edge_type_settings_widget()

    for row in edge.create_edge_toggles():
        type_widget.layout().addLayout(row)

    routing_widget = edge.create_edge_routing_settings_widget()
    settings.add_content_widget(routing_widget)
    settings.add_content_widget(type_widget)


def set_active_edge(
    edge_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    scene_view: Type[gv_tool.SceneView],
    edge: Type[gv_tool.Edge],
    window: Type[gv_tool.Window],
):
    view = scene_view.get_view()
    edge.set_active_edge(edge_type)
    if edge_type:
        style_sheet = edge.get_edge_stylesheet(edge_type)
    else:
        window.set_status("")

        style_sheet = ""
    view.setStyleSheet(style_sheet)
    text = QCoreApplication.translate("GraphViewer", "Create {} Relationship").format(edge_type)
    window.set_status(text)


def create_relation(
    start_node: Node,
    end_node: Node,
    relation_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
):
    from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants

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
    p.setPen(edge.create_pen_for_edgestyle(edge_legend._edge_type))
    p.drawLine(int(x1), int(y), int(x2), int(y))


def update_path(focus_edge: ui.Edge, edge: Type[gv_tool.Edge], scene_view: Type[gv_tool.SceneView]):
    # Determine routing mode from scene
    sc = scene_view.get_scene()
    orth = False
    try:
        orth = bool(getattr(sc, "orthogonal_edges", False))
    except Exception:
        orth = False

    # Compute anchors on node boundaries

    path = QPainterPath()
    if not edge.is_orthogonal_mode():
        p_start = edge._calculate_anchor_on_node(focus_edge.start_node, focus_edge.end_node.pos())
        p_end_tip = edge._calculate_anchor_on_node(focus_edge.end_node, focus_edge.start_node.pos())
        last_base = edge.draw_straight_line(path, p_start, p_end_tip)

    else:
        horizontal_mode = edge._ortho_mode_is_hor(focus_edge.start_node, focus_edge.end_node.pos())
        p_start = edge._ortho_start(
            focus_edge.start_node, focus_edge.end_node.pos(), horizontal_mode
        )
        p_end_tip = edge._ortho_start(
            focus_edge.end_node, focus_edge.start_node.pos(), horizontal_mode
        )
        last_base = edge.draw_ortho_line(path, p_start, p_end_tip, horizontal_mode)

    focus_edge.setPath(path)
    # Arrow head aligned with the last segment direction
    focus_edge._arrow_polygon = edge._compute_arrow(last_base, p_end_tip)


def paint_path(painter: QPainter, focus_edge: ui.Edge, edge: Type[gv_tool.Edge]):
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setBrush(QBrush(Qt.NoBrush))
    path = focus_edge.path()

    # Custom selection visualization: soft glow under the edge instead of Qt's default rectangle
    if focus_edge.isSelected():
        glow_pen = edge.get_selected_pen(focus_edge)
        painter.setPen(glow_pen)
        painter.drawPath(path)
        # Glow around arrow outline too
        if focus_edge._arrow_polygon is not None and not focus_edge._arrow_polygon.isEmpty():
            painter.drawPolygon(focus_edge._arrow_polygon)

    # Draw the edge with its configured style
    painter.setPen(focus_edge.pen())
    painter.drawPath(path)

    # Draw arrow head on top (solid outline)
    if focus_edge._arrow_polygon is not None and not focus_edge._arrow_polygon.isEmpty():
        solid_pen = QPen(focus_edge.pen())
        try:
            solid_pen.setStyle(Qt.SolidLine)
        except Exception:
            pass
        painter.setPen(solid_pen)
        painter.drawPolygon(focus_edge._arrow_polygon)
