from __future__ import annotations
from PySide6.QtCore import Qt, QRectF, QPointF, QCoreApplication
from PySide6.QtGui import QMouseEvent, QDropEvent
from typing import TYPE_CHECKING, Type

import qtawesome as qta
from bsdd_gui.plugins.graph_viewer.module.scene_view import constants
from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import BsddClass, BsddProperty

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.scene_view import ui
    from bsdd_gui.plugins.graph_viewer.module.window import ui as ui_window
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from bsdd_gui.module.property_table_widget.ui import PropertyWidget


def connect_signals(
    window: Type[gv_tool.Window],
    scene_view: Type[gv_tool.SceneView],
    settings: Type[gv_tool.Settings],
    physics: Type[gv_tool.Physics],
):
    window.signals.widget_created.connect(lambda w: handle_widget_creation(w, scene_view))
    window.signals.delete_selection_requested.connect(scene_view.request_delete_selection)
    scene_view.connect_internal_signals()
    settings.signals.widget_created.connect(lambda sw: add_settings(scene_view, settings))
    physics.signals.is_running_changed.connect(scene_view.request_retranslate)


def add_settings(scene_view: Type[gv_tool.SceneView], settings: Type[gv_tool.Settings]):
    widget = scene_view.create_button_widget()
    scene_view.connect_button_settings()
    settings.add_content_widget(widget)


def retranslate_ui(scene_view: Type[gv_tool.SceneView], phyiscs: Type[gv_tool.Physics]):
    scene = scene_view.get_scene()
    if not scene:
        return
    button_widget = scene_view.get_buttons_widget()
    button_widget.retranslateUi(button_widget)
    pause_text = QCoreApplication.translate("GraphView", "Pause")
    play_text = QCoreApplication.translate("GraphView", "Play")
    button_widget.bt_start_stop.setText(pause_text if phyiscs.is_running() else play_text)
    icon = qta.icon("mdi6.pause") if phyiscs.is_running() else qta.icon("mdi6.play")
    button_widget.bt_start_stop.setIcon(icon)


def handle_widget_creation(widget: ui_window.GraphWidget, scene_view: Type[gv_tool.SceneView]):
    scene_view.set_view(widget.view)
    widget.view.setScene(scene_view.create_scene())
    scene_view.create_scene_rect()
    scene_view.create_help_overlay()
    scene_view.connect_view()


def center_scene(node: Type[gv_tool.Node], scene_view: Type[gv_tool.SceneView]):
    scene = scene_view.get_scene()
    view = scene_view.get_view()
    if scene is None:
        return
    # Fit to visible nodes if any, with a small buffer
    vis = [n for n in node.get_nodes() if n.isVisible()]
    items = vis if vis else node.get_nodes()
    if not items:
        # Fallback to a reasonable default area
        scene.setSceneRect(QRectF(-500, -500, 1000, 1000))
        return
    xs = [n.pos().x() for n in items]
    ys = [n.pos().y() for n in items]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    pad = 120.0
    w = max(1.0, (maxx - minx)) + 2 * pad
    h = max(1.0, (maxy - miny)) + 2 * pad
    # scene.setSceneRect()
    view.fitInView(QRectF(minx - pad, miny - pad, w, h), Qt.KeepAspectRatio)


def delete_selection(
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
):
    scene = scene_view.get_scene()
    bsdd_dictionary = project.get()
    selected_nodes, selected_edges = scene_view.get_selected_items()
    edges_to_remove = list(set(selected_edges))
    for e in edges_to_remove:
        edge.remove_edge(edge, scene, bsdd_dictionary)

    for n in selected_nodes:
        node.remove_node(n, scene, ignored_edges=edges_to_remove)

    scene_view.request_recalculate_edges()


def resize_event(event, scene_view: Type[gv_tool.SceneView]):
    scene_view.reposition_help_overlay()


def double_click_event(
    event: QMouseEvent, scene_view: Type[gv_tool.SceneView], node: Type[gv_tool.Node]
):
    pos_view = scene_view._event_qpoint(event)
    item = scene_view._item_at_pos(pos_view)
    node = node._node_from_item(item)
    if node is None:
        return True
    node.emit_node_double_clicked(node)
    event.accept()
    return False


def mouse_press_event(
    event: QMouseEvent,
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    try:
        pos_view = scene_view._event_qpoint(event)
        pos_scene = view.mapToScene(pos_view)
    except Exception:
        pass

    middle_pressed = event.button() == Qt.MouseButton.MiddleButton
    left_clicked = event.button() == Qt.MouseButton.LeftButton
    shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

    if middle_pressed:
        # Start manual panning with middle mouse
        scene_view.set_panning_mmb(True)
        scene_view.set_pan_last_pos(scene_view._event_qpoint(event))
        try:
            view.setCursor(Qt.CursorShape.ClosedHandCursor)
        except Exception:
            pass
        event.accept()
        return False

    elif left_clicked and shift_pressed:
        # Begin edge drawing if pressed on a Node
        pos_view = scene_view._event_qpoint(event)
        item = scene_view._item_at_pos(pos_view)
        n = node._node_from_item(item)
        if n is None:
            return False
        scene_pos = view.mapToScene(pos_view)
        edge._start_edge_drag(n, scene_pos)
        event.accept()
    return True


def mouse_release_event(
    event: QMouseEvent,
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    if scene_view.get_panning_mmb() and event.button() == Qt.MiddleButton:
        scene_view.set_panning_mmb(False)
        scene_view.set_pan_last_pos(None)
        try:
            view.setCursor(Qt.ArrowCursor)
        except Exception:
            pass
        event.accept()
        return False
    elif edge.is_edge_drag_active() and event.button() == Qt.LeftButton:
        pos_view = scene_view._event_qpoint(event)
        item = scene_view._item_at_pos(pos_view)
        n = node._node_from_item(item)
        edge._finish_edge_drag(n)
        event.accept()
        return False
    return True


def mouse_move_event(
    event: QMouseEvent,
    scene_view: Type[gv_tool.SceneView],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    if scene_view.get_panning_mmb():
        # Drag the view by adjusting scrollbars
        cur = scene_view._event_qpoint(event)
        if scene_view.get_pan_last_pos() is not None and cur is not None:
            delta = cur - scene_view.get_pan_last_pos()
            try:
                view.horizontalScrollBar().setValue(
                    view.horizontalScrollBar().value() - int(delta.x())
                )
                view.verticalScrollBar().setValue(view.verticalScrollBar().value() - int(delta.y()))
            except Exception:
                pass
        scene_view.set_pan_last_pos(cur)
        event.accept()
        return False
    if edge.is_edge_drag_active():
        pos_view = scene_view._event_qpoint(event)
        scene_pos = view.mapToScene(pos_view)
        edge._update_edge_drag(scene_pos)
        event.accept()
        return False
    return True


def drag_enter_event(event, scene_view: Type[gv_tool.SceneView]):
    if scene_view._mime_has_bsdd_class(event.mimeData()):
        event.acceptProposedAction()
        return False

    else:
        return True


def drag_move_event(event, scene_view: Type[gv_tool.SceneView]):
    if scene_view._mime_has_bsdd_class(event.mimeData()):
        event.acceptProposedAction()
        return False
    else:
        return True


def drop_event(
    event: QDropEvent,
    scene_view: Type[gv_tool.SceneView],
    class_tree: Type[tool.ClassTreeView],
    property_table: Type[tool.PropertyTableWidget],
    project: Type[tool.Project],
):
    mime_data = event.mimeData()
    mime_type = scene_view.get_mime_type(mime_data)
    if mime_type is None:
        event.ignore()
        return
    scene_pos = scene_view.get_position_from_event(event)
    bsdd_dictionary = project.get()

    classes_to_add: list[BsddClass] = list()
    properties_to_add = list()
    if mime_type == constants.CLASS_DRAG:
        payload = class_tree.get_payload_from_data(mime_data)
        classes_to_add += scene_view.read_classes_to_add(payload, bsdd_dictionary)

    elif mime_type == constants.PROPERTY_DRAG:
        payload = property_table.get_payload_from_data(mime_data)
        properties_to_add += scene_view.read_properties_to_add(payload, bsdd_dictionary)

    if not classes_to_add and not properties_to_add:
        event.ignore()

    scene_view.request_classes_insert(classes_to_add, scene_pos)
    scene_view.request_properties_insert(properties_to_add, scene_pos)

    scene_view.request_recalculate_edges()
    event.acceptProposedAction()


def insert_classes_in_scene(
    classes: list[BsddClass],
    position: QPointF,
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    ifc_helper: Type[tool.IfcHelper],
    project: Type[tool.Project],
):
    ifc_classes = {c.get("code"): c for c in ifc_helper.get_classes()}
    bsdd_dictionary = project.get()
    scene = scene_view.get_scene()

    if position is None:
        position = QPointF(scene.sceneRect().width() / 2, scene.sceneRect().height() / 2)
    offset_step = QPointF(24.0, 18.0)
    cur_position = QPointF(position)

    external_nodes = node.get_external_nodes()
    internal_nodes = node.get_internal_nodes(bsdd_dictionary)

    for bsdd_class in classes:
        class_uri = cl_utils.build_bsdd_uri(bsdd_class, bsdd_dictionary)
        if class_uri not in internal_nodes:
            new_node = node.add_node(bsdd_class, pos=cur_position, is_external=False)
            internal_nodes[class_uri] = new_node
            cur_position += offset_step

        ifc_entities = bsdd_class.RelatedIfcEntityNamesList or []
        for e in ifc_entities:
            new_node = node.add_ifc_node(e, cur_position, ifc_classes, external_nodes)
            if new_node:
                cur_position += offset_step
                external_nodes[new_node.bsdd_data.OwnedUri] = new_node.bsdd_data

        for class_relation in bsdd_class.ClassRelations:
            related_uri = class_relation.RelatedClassUri
            if related_uri in external_nodes or related_uri in internal_nodes:
                continue

            related_bsdd_class = cl_utils.get_class_by_uri(bsdd_dictionary, related_uri)
            if related_bsdd_class.OwnedUri and cl_utils.is_external_ref(
                related_bsdd_class.OwnedUri, bsdd_dictionary
            ):
                new_node = node.add_node(related_bsdd_class, pos=cur_position, is_external=True)
                external_nodes[related_bsdd_class.OwnedUri] = new_node.bsdd_data

            else:
                new_node = node.add_node(related_bsdd_class, pos=cur_position, is_external=False)
                uri = cl_utils.build_bsdd_uri(related_bsdd_class, bsdd_dictionary)
                internal_nodes[uri] = new_node.bsdd_data
            cur_position += offset_step


def insert_properties_in_scene(
    bsdd_properties: list[BsddProperty],
    position: QPointF,
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    project: Type[tool.Project],
):
    scene = scene_view.get_scene()
    bsdd_dictionary = project.get()
    if position is None:
        position = QPointF(scene.sceneRect().width() / 2, scene.sceneRect().height() / 2)

    offset_step = QPointF(24.0, 18.0)
    cur_position = QPointF(position)

    external_nodes = node.get_external_nodes()
    internal_nodes = node.get_internal_nodes(bsdd_dictionary)

    for bsdd_property in bsdd_properties:
        prop_uri = prop_utils.build_bsdd_uri(bsdd_property, bsdd_dictionary)
        if prop_uri not in internal_nodes:
            new_node = node.add_node(bsdd_property, pos=cur_position, is_external=False)
            internal_nodes[prop_uri] = new_node
            cur_position += offset_step

        for property_relation in bsdd_property.PropertyRelations:
            related_uri = property_relation.RelatedPropertyUri
            if related_uri in external_nodes or related_uri in internal_nodes:
                continue

            related_bsdd_property = prop_utils.get_property_by_uri(related_uri, bsdd_dictionary)
            if related_bsdd_property.OwnedUri and dict_utils.is_external_ref(
                related_bsdd_property.OwnedUri, bsdd_dictionary
            ):
                new_node = node.add_node(related_bsdd_property, pos=cur_position, is_external=True)
                external_nodes[related_bsdd_property.OwnedUri] = new_node.bsdd_data
            else:
                new_node = node.add_node(related_bsdd_property, pos=cur_position, is_external=False)
                uri = cl_utils.build_bsdd_uri(related_bsdd_property, bsdd_dictionary)
                internal_nodes[uri] = new_node.bsdd_data
            cur_position += offset_step


def recalculate_edges(
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
    project: Type[tool.Project],
):
    bsdd_dict = project.get()
    scene = scene_view.get_scene()
    if not scene:
        return
    nodes = node.get_nodes()
    relations_dict = edge.get_relations_dict(bsdd_dict)
    uri_dict = node.get_uri_dict(bsdd_dict)

    new_edges = edge.find_class_relations(nodes, uri_dict, relations_dict, bsdd_dict)
    new_edges += edge.find_class_property_relations(nodes, uri_dict, relations_dict, bsdd_dict)
    new_edges += edge.find_property_relations(nodes, uri_dict, relations_dict, bsdd_dict)
    new_edges += edge.find_ifc_relations(nodes, uri_dict, relations_dict, bsdd_dict)
    for e in new_edges:
        edge.add_edge(e)
        relations_dict[e.edge_type][edge._info(e.start_node, e.end_node, bsdd_dict)] = e

    scene_view.apply_filters(edge.get_filters(), node.get_filters())
