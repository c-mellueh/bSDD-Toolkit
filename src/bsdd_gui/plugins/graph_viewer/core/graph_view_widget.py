from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, QPointF
from PySide6.QtWidgets import QWidget, QMessageBox, QLineEdit
from PySide6.QtGui import QDropEvent
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget import constants, ui_settings_widget
from bsdd_json import (
    BsddClass,
    BsddProperty,
    BsddClassProperty,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import class_utils as class_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from random import random
from bsdd_gui.module.ifc_helper.data import IfcHelperData
import webbrowser
import json
import logging
import qtawesome as qta

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.view_ui import GraphView, GraphScene
    from bsdd_gui.plugins.graph_viewer.module.graph_view_widget import graphics_items, ui

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_table_widget.ui import PropertyWidget
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
import qtawesome as qta

def remove_main_menu_actions(
    window: Type[gv_tool.GraphViewWidget], main_window: Type[tool.MainWindowWidget]
):
    return #Moved to core.MainWiindow

def connect_signals(
    graph_view: Type[gv_tool.GraphViewWidget],
    relationship_editor: Type[tool.RelationshipEditorWidget],
    class_property_table: Type[tool.ClassPropertyTableView],
    property_set_table: Type[tool.PropertySetTableView],
    project: Type[tool.Project],
):
    return None #Moved to Edge and Node


def connect_to_main_window(
    graph_view: Type[gv_tool.GraphViewWidget], main_window: Type[tool.MainWindowWidget]
):
    return None #Moved to Window

def add_icons(widget: ui.GraphWindow):
    return None #Moved to SceneView 




def enter_window(
    window: ui.GraphWindow, graph_view: gv_tool.GraphViewWidget, project: Type[tool.Project]
):
    return #Moved to core.Inputbar

def popuplate_widget(
    graph_view: Type[gv_tool.GraphViewWidget],
    project: Type[tool.Project],
    ifc_helper: Type[tool.IfcHelper],
):
    return None # Moved to core.SceneView


def handle_drop_event(
    event: QDropEvent,
    view: GraphView,
    graph_view: Type[gv_tool.GraphViewWidget],
    class_tree: Type[tool.ClassTreeView],
    property_table: Type[tool.PropertyTableWidget],
    project: Type[tool.Project],
    ifc_helper: Type[tool.IfcHelper],
):
    return None #core.SceneView


def recalculate_edges(graph_view: Type[gv_tool.GraphViewWidget], project: Type[tool.Project]):
    return None #core.SceneView


def node_double_clicked(
    node: graphics_items.Node,
    property_table: Type[tool.PropertyTableWidget],
    class_tree: Type[tool.ClassTreeView],
    main_window: Type[tool.MainWindowWidget],
):
    return None #Moved to Node

def create_relation(
    start_node: graphics_items.Node,
    end_node: graphics_items.Node,
    relation_type: constants.ALLOWED_EDGE_TYPES_TYPING,
    graph_view: Type[gv_tool.GraphViewWidget],
    project: Type[tool.Project],
):
    return None# Moved to Edge


def export_graph(
    graph_view: Type[gv_tool.GraphViewWidget], popups: Type[tool.Popups], appdata: Type[tool.Appdata]
):
    return None #Moved to Scene


def import_graph(
    graph_view: Type[gv_tool.GraphViewWidget],
    project: Type[tool.Project],
    popups: Type[tool.Popups],
    appdata: Type[tool.Appdata],
    ifc_helper: Type[tool.IfcHelper],
):

    return None # Moved to Scene


def buchheim(graph_view: Type[gv_tool.GraphViewWidget], project: Type[tool.Project]):
    allowed = graph_view.reset_children_dict()
    if not allowed:
        # Inform the user that an edge type must be selected
        try:
            w = graph_view.get_widget()
            title = QCoreApplication.translate("GraphView", "Create Tree")
            msg = QCoreApplication.translate(
                "GraphView",
                "Select an edge type in the sidebar (Edge Types) by double-clicking the legend to activate it, then run Create Tree.",
            )
            QMessageBox.information(w, title, msg)
        except Exception:
            pass
        return
    graph_view.pause()
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
    graph_view.remove_node(helper_node, project.get())
    graph_view.center_scene()


def add_node_by_lineinput(
    window: ui.GraphWindow,
    graph_view: Type[gv_tool.GraphViewWidget],
    project: Type[tool.Project],
    ifc_helper: Type[tool.IfcHelper],
):
  return None#Moved to core.inputbar