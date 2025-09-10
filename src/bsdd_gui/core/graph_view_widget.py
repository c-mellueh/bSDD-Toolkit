from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, QPointF
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QDropEvent
from bsdd_gui.module.graph_view_widget import constants, ui_settings_widget
from bsdd_json import (
    BsddClass,
    BsddProperty,
    BsddClassProperty,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_json.utils import property_utils as prop_utils
import json
import logging

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.view_ui import GraphView, GraphScene
    from bsdd_gui.module.graph_view_widget import graphics_items, ui

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_table_widget.ui import PropertyWidget


def connect_signals(
    graph_view: Type[tool.GraphViewWidget],
    relationship_editor: Type[tool.RelationshipEditorWidget],
    class_property_table: Type[tool.ClassPropertyTableView],
    property_set_table: Type[tool.PropertySetTableView],
    project: Type[tool.Project],
):
    graph_view.connect_internal_signals()

    def handle_rel_update(edge: graphics_items.Edge):
        start_data = edge.start_node.bsdd_data
        widget = relationship_editor.get_widget(start_data)
        if not widget:
            return
        relationship_editor.reset_view(widget.tv_relations)

    def handle_prop_update(*args, **kwargs):
        class_property_table.reset_views()
        property_set_table.reset_views()

    graph_view.signals.new_edge_created.connect(handle_rel_update)
    graph_view.signals.edge_removed.connect(handle_rel_update)

    graph_view.signals.new_class_property_created.connect(handle_prop_update)
    graph_view.signals.class_property_removed.connect(handle_prop_update)

    def handle_remove(bsdd_data):
        if isinstance(bsdd_data, BsddClassProperty):
            bsdd_data = prop_utils.get_internal_property(bsdd_data)
        if not bsdd_data:
            return
        node = graph_view.get_node_from_bsdd_data(bsdd_data)
        if not node:
            return
        graph_view.remove_node(node)

    def handle_relation_remove(relation: BsddClassRelation | BsddPropertyRelation):
        edge = graph_view.get_edge_from_relation(relation, project.get())
        if edge is None:
            return
        graph_view.remove_edge(edge, only_visual=True, allow_parent_deletion=True)

    def handle_relation_add(relation: BsddClassRelation | BsddPropertyRelation):
        start_data, end_data, relation_type = graph_view.read_relation(relation, project.get())
        start_node = graph_view.get_node_from_bsdd_data(start_data)
        end_node = graph_view.get_node_from_bsdd_data(end_data)
        if not (start_node and end_node):
            return
        edge = graph_view.create_edge(start_node, end_node, edge_type=relation_type)
        graph_view.add_edge(graph_view.get_scene(), edge)

    project.signals.class_removed.connect(handle_remove)
    project.signals.property_removed.connect(handle_remove)
    project.signals.class_property_removed.connect(handle_remove)
    project.signals.class_relation_added.connect(handle_relation_add)
    project.signals.class_relation_removed.connect(handle_relation_remove)
    project.signals.property_relation_added.connect(handle_relation_add)
    project.signals.property_relation_removed.connect(handle_relation_remove)

    def handle_edge_add(edge: graphics_items.Edge):
        relation = graph_view.get_relation_from_edge(edge, project.get())
        if isinstance(relation, BsddClassRelation):
            project.signals.class_relation_added.emit(relation)
        if isinstance(relation, BsddClassRelation):
            project.signals.property_relation_added.emit(relation)

    graph_view.signals.new_edge_created.connect(handle_edge_add)


def connect_to_main_window(
    graph_view: Type[tool.GraphViewWidget], main_window: Type[tool.MainWindowWidget]
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action(None, "Graph View", lambda: graph_view.request_widget())
    graph_view.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    graph_view: Type[tool.GraphViewWidget], main_window: Type[tool.MainWindowWidget]
):
    action = graph_view.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GraphView", "Graph View"))


def create_widget(
    parent: QWidget | None,
    graph_view: Type[tool.GraphViewWidget],
    main_window: Type[tool.MainWindowWidget],
):
    # Default parent to the main window if not provided
    w = graph_view.get_widget()
    if w is None:
        if parent is None:
            parent = main_window.get()
        w = graph_view.create_widget()
        graph_view.register_widget(w)
        # Show as independent window
    w.show()
    w.activateWindow()
    w.raise_()
    return w


def register_widget(widget, graph_view: Type[tool.GraphViewWidget]):
    graph_view.register_widget(widget)


def connect_widget(widget: ui.GraphWindow, graph_view: Type[tool.GraphViewWidget]):
    graph_view.connect_widget_signals(widget)


def popuplate_widget(graph_view: Type[tool.GraphViewWidget], project: Type[tool.Project]):
    widget = graph_view.get_widget()
    if widget is None:
        return
    bsdd_dictionary = project.get()
    graph_view.clear_scene()
    position = QPointF(0.0, 0.0)
    graph_view.insert_classes_in_scene(graph_view.get_scene(), bsdd_dictionary.Classes, position)
    widget._apply_filters()
    graph_view.center_scene()
    position += QPointF(40.0, 40.0)
    graph_view.insert_properties_in_scene(
        graph_view.get_scene(), bsdd_dictionary.Properties, position
    )
    recalculate_edges(graph_view, project)


def handle_drop_event(
    event: QDropEvent,
    view: GraphView,
    graph_view: Type[tool.GraphViewWidget],
    class_tree: Type[tool.ClassTreeView],
    property_table: Type[tool.PropertyTableWidget],
    project: Type[tool.Project],
):
    mime_data = event.mimeData()
    mime_type = graph_view.get_mime_type(mime_data)
    if mime_type is None:
        event.ignore()
        return
    scene_pos = graph_view.get_position_from_event(event, view)
    bsdd_dictionary = project.get()

    classes_to_add = list()
    properties_to_add = list()
    if mime_type == constants.CLASS_DRAG:
        payload = class_tree.get_payload_from_data(mime_data)
        classes_to_add += graph_view.read_classes_to_add(payload, bsdd_dictionary)

    elif mime_type == constants.PROPERTY_DRAG:
        payload = property_table.get_payload_from_data(mime_data)
        properties_to_add += graph_view.read_properties_to_add(payload, bsdd_dictionary)

    if not classes_to_add and not properties_to_add:
        event.ignore()
        return

    scene = view.scene()
    new_class_nodes = graph_view.insert_classes_in_scene(scene, classes_to_add, scene_pos)
    new_property_nodes = graph_view.insert_properties_in_scene(scene, properties_to_add, scene_pos)
    recalculate_edges(graph_view, project)
    event.acceptProposedAction()


def recalculate_edges(graph_view: Type[tool.GraphViewWidget], project: Type[tool.Project]):
    bsdd_dictionary = project.get()
    scene: GraphScene = graph_view.get_scene()
    if not scene:
        return
    nodes = scene.nodes
    edges = scene.edges
    class_codes, full_class_uris, property_codes, full_property_uris, relations_dict = (
        graph_view.get_code_dicts(scene, bsdd_dictionary)
    )
    new_edges = graph_view.find_class_relations(nodes, class_codes, full_class_uris, relations_dict)
    new_edges += graph_view.find_class_property_relations(nodes, property_codes, relations_dict)
    new_edges += graph_view.find_property_relations(
        nodes, property_codes, full_property_uris, relations_dict
    )
    for edge in new_edges:
        graph_view.add_edge(scene, edge)
        relations_dict[edge.edge_type][graph_view._info(edge.start_node, edge.end_node)] = edge
    graph_view.get_widget()._apply_filters()


def node_double_clicked(
    node: graphics_items.Node,
    property_table: Type[tool.PropertyTableWidget],
    class_tree: Type[tool.ClassTreeView],
    main_window: Type[tool.MainWindowWidget],
):
    if node.node_type == constants.CLASS_NODE_TYPE:
        bsdd_cass: BsddClass = node.bsdd_data
        class_tree.select_and_expand(bsdd_cass, main_window.get_class_view())
        main_window.get().raise_()
        main_window.get().activateWindow()

    elif node.node_type == constants.PROPERTY_NODE_TYPE:
        bsdd_property: BsddProperty = node.bsdd_data
        property_table.request_widget()
        widget: PropertyWidget = property_table.get_widgets()[-1]
        property_table.select_property(bsdd_property, widget.tv_properties)


def create_relation(
    start_node: graphics_items.Node,
    end_node: graphics_items.Node,
    relation_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    graph_view: Type[tool.GraphViewWidget],
    project: Type[tool.Project],
):

    if start_node.node_type == constants.CLASS_NODE_TYPE:
        if end_node.node_type == constants.PROPERTY_NODE_TYPE:
            if relation_type == constants.C_P_REL:
                graph_view.create_class_property_relation(start_node, end_node, project.get())
        elif end_node.node_type == constants.CLASS_NODE_TYPE:
            graph_view.create_class_class_relation(
                start_node, end_node, project.get(), relation_type
            )
    elif start_node.node_type == constants.PROPERTY_NODE_TYPE:
        if end_node.node_type == constants.CLASS_NODE_TYPE:
            graph_view.create_class_property_relation(start_node, end_node, project.get())
        elif end_node.node_type == constants.PROPERTY_NODE_TYPE:
            graph_view.create_property_property_relation(
                start_node, end_node, project.get(), relation_type
            )
    widget = graph_view.get_widget()
    widget._apply_filters()


def delete_selection(graph_view: Type[tool.GraphViewWidget]):
    sc = graph_view.get_scene()
    # Collect selected items
    nodes_to_remove, edges_to_remove = graph_view.get_selected_items()

    # Deduplicate
    edges_to_remove = list(set(edges_to_remove))

    # Remove edges first
    for e in edges_to_remove:
        graph_view.remove_edge(e)
    # Remove nodes
    for n in nodes_to_remove:
        graph_view.remove_node(n, ignored_edges=edges_to_remove)


def export_graph(
    graph_view: Type[tool.GraphViewWidget], popups: Type[tool.Popups], appdata: Type[tool.Appdata]
):
    widget = graph_view.get_widget()
    if widget is None:
        return
    last_path = appdata.get_path(constants.PATH_NAME) or "graph_layout.json"
    text = QCoreApplication.translate("Graph View", "Export Graph View")
    path = popups.get_save_path(constants.FILETYPE, graph_view.get_widget(), last_path, text)
    if not path:
        return
    appdata.set_path(constants.PATH_NAME, path)
    payload = graph_view._collect_layout()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        try:
            widget.statusbar.showMessage(
                QCoreApplication.translate("GraphView", "Layout exported: ") + str(path),
                3000,
            )
        except Exception:
            pass
    except Exception as e:
        logging.exception("Failed to export layout: %s", e)


def import_graph(
    graph_view: Type[tool.GraphViewWidget],
    project: Type[tool.Project],
    popups: Type[tool.Popups],
    appdata: Type[tool.Appdata],
):

    widget = graph_view.get_widget()
    if widget is None:
        return
    last_path = appdata.get_path(constants.PATH_NAME) or "graph_layout.json"
    title = QCoreApplication.translate("Graph View", "Export Graph View")

    path = popups.get_open_path(constants.FILETYPE, graph_view.get_widget(), last_path, title)
    if not path:
        return
    appdata.set_path(constants.PATH_NAME, path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logging.exception("Failed to load layout: %s", e)
        return

    # Resolve bsDD dictionary from current project lazily to avoid import cycles
    bsdd_dict = project.get()
    if not isinstance(data, dict) or "nodes" not in data:
        return

    # Clear current scene
    graph_view.clear_scene()
    scene = graph_view.get_scene()
    if scene is None:
        return

    imported_nodes: list[graphics_items.Node] = []
    for item in data.get("nodes", []) or []:
        node = graph_view.import_node_from_json(item, project.get())
        if node is not None:
            imported_nodes.append(node)
    # Recreate implied edges based on current dictionary relationships
    recalculate_edges(graph_view, project)  # type: ignore[name-defined]
    try:
        widget.statusbar.showMessage(
            QCoreApplication.translate("GraphView", "Layout imported: ") + str(path),
            3000,
        )
    except Exception:
        pass


def buchheim(graph_view: Type[tool.GraphViewWidget]):
    graph_view.pause()
    graph_view.reset_children_dict()
    roots = graph_view.find_roots()
    root = roots[0]
    all_nodes = graph_view.get_scene().nodes
    graph_view.intialize(root)
    root_x_pos = [n.pos().x() for n in roots]
    root_y_pos = [n.pos().y() for n in roots]
    root_mid_x = (min(root_x_pos) + max(root_x_pos)) / 2
    root_mid_y = (min(root_y_pos) + max(root_y_pos)) / 2
    min_x = max(min(n.pos().x() for n in all_nodes), 500.0)
    min_y = max(min(n.pos().y() for n in all_nodes), 500.0)
    center_pos = QPointF(root_mid_x, root_mid_y)
    helper_node = graph_view.add_node(graph_view.get_scene(), None, center_pos)

    graph_view.get_properties().children_dict[helper_node] = roots
    for r in roots:
        graph_view.get_properties().parent_dict[r] = helper_node

    graph_view.intialize(helper_node)
    graph_view.buchheim(helper_node)
    graph_view.rearrange(helper_node, QPointF(min_x, min_y))
    graph_view.remove_node(helper_node)
    graph_view.center_scene()