from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QDropEvent
from bsdd_gui.module.graph_view_widget import constants, ui_settings_widget
from bsdd_json import BsddClass, BsddProperty

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.view_ui import GraphView, GraphScene
    from bsdd_gui.module.graph_view_widget import graphics_items, ui

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_table_widget.ui import PropertyWidget

def connect_signals(graph_view: Type[tool.GraphViewWidget]):
    graph_view.connect_internal_signals()


def connect_to_main_window(
    graph_view: Type[tool.GraphViewWidget], main_window: Type[tool.MainWindowWidget]
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action("menuData", "Graph View", lambda: graph_view.request_widget())
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
    graph_view.clear_scene()
    graph_view.populate_from_bsdd(widget, project.get())


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
    recalculate_relationships(view, graph_view, project)
    event.acceptProposedAction()


def recalculate_relationships(
    view: GraphView, graph_view: Type[tool.GraphViewWidget], project: Type[tool.Project]
):
    bsdd_dictionary = project.get()

    scene: GraphScene = view.scene()
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
        bsdd_property:BsddProperty = node.bsdd_data
        property_table.request_widget()
        widget:PropertyWidget = property_table.get_widgets()[-1]
        property_table.select_property(bsdd_property,widget.tv_properties)