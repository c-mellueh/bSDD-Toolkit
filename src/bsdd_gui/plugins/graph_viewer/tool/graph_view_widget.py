from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypedDict
import logging

from PySide6.QtGui import QDropEvent, QColor
from PySide6.QtWidgets import QWidget, QFileDialog, QCompleter
from PySide6.QtCore import QPointF, QCoreApplication, QRectF, Qt
import json

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, WidgetTool
from bsdd_gui.presets.signal_presets import WidgetSignals
from PySide6.QtCore import Signal
import qtawesome as qta
import random
from bsdd_gui.module.ifc_helper.data import IfcHelperData

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.prop import (
        GraphViewWidgetProperties,
    )
from bsdd_json import (
    BsddDictionary,
    BsddClass,
    BsddProperty,
    BsddClassProperty,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils

from bsdd_gui.plugins.graph_viewer.module.graph_view_widget import (
    trigger,
    ui,
    constants,
    ui_settings_widget,
    graphics_items,
    view_ui,
)
from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.graphics_items import Node
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import JSON_MIME as PROPERTY_JSON_MIME


class InfoDict(TypedDict):
    start_uri: str
    end_uri: str
    start_node_type: str
    end_node_type: str


RelationsDict = None #Moved To tool.Edge

class Signals(WidgetSignals):
    # Emitted when a graph node is double-clicked in the view.
    # Payload: the Node graphics item (access bsdd_data via node.bsdd_data)
    node_double_clicked = Signal(object)
    new_class_property_created = Signal(BsddClassProperty)
    class_property_removed = Signal(BsddClassProperty, BsddClass)
    new_edge_created = Signal(graphics_items.Edge)
    edge_removed = Signal(graphics_items.Edge)
    class_relation_removed = Signal(BsddClassRelation)
    property_relation_removed = Signal(BsddPropertyRelation)
    ifc_reference_removed = Signal(BsddClass, str)  # BsddClass, IfcRelationName
    ifc_reference_added = Signal(BsddClass, str)  # BsddClass, IfcRelationName


class GraphViewWidget(ActionTool, WidgetTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewWidgetProperties:
        return bsdd_gui.GraphViewWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        # Lazy import to avoid heavy cost on module load
        from bsdd_gui.plugins.graph_viewer.module.graph_view_widget.ui import GraphWindow
        return GraphWindow


    @classmethod
    def connect_widget_signals(cls, widget: ui.GraphWindow):
        return None # Moved to tool.SceneView

    @classmethod
    def create_widget(cls, *args, parent=None, **kwargs):
        # Pass parent through so the window is owned by the caller (e.g., main window)
        widget: ui.GraphWindow = super().create_widget(*args, parent=parent, **kwargs)
        return widget

    @classmethod
    def get_widget(cls) -> ui.GraphWindow:
        if not cls.get_widgets():
            return None
        return cls.get_widgets()[-1]

    ### Drag and Drop

    @classmethod
    def get_mime_type(cls, mime_data) -> constants.ALLOWED_DRAG_TYPES | None:
        return None #Move to SceneView

    @classmethod
    def get_position_from_event(cls, event: QDropEvent, gv: view_ui):
        return None #moved to ScenView

    @classmethod
    def read_classes_to_add(cls, payload: dict, bsdd_dictionary: BsddDictionary):
        return None#moved to ScenView

    @classmethod
    def read_properties_to_add(cls, payload: dict, bsdd_dictionary: BsddDictionary):
        return None # Moved to SceneView

    @classmethod
    def add_edge(
        cls,
        scene: view_ui.GraphScene,
        edge: graphics_items.Edge,
    ) -> graphics_items.Edge:

        return None # tool.Edge
    
    @classmethod
    def add_node(
        cls,
        scene: view_ui.GraphScene,
        bsdd_data: BsddClass | BsddProperty,
        pos: Optional[QPointF] = None,
        color: Optional[QColor] = None,
        is_external=False,
    ) -> Node:

        return None #Moved to Node

    @classmethod
    def insert_classes_in_scene(
        cls,
        bsdd_dictionary: BsddDictionary,
        scene: view_ui.GraphScene,
        classes: list[BsddClass],
        position: QPointF = None,
        ifc_classes: dict[str, dict[str, str]] = dict(),
    ):
        return #Moved to core.SceneView

    @classmethod
    def add_ifc_node(
        cls, ifc_code: str, position: QPointF, ifc_classes: dict = None, external_nodes=None
    ):
        return None # Moved To Node


    @classmethod
    def _info(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
    ):
        return None #Moved to tool.Edge

    @classmethod
    def get_uri_dicts(cls, scene: view_ui.GraphScene, bsdd_dictionary: BsddDictionary):
        return None #Splittet to tool.Node and tool.Edge

    @classmethod
    def find_class_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], graphics_items.Edge]],
        bsdd_dictionary: BsddDictionary,
    ) -> list[graphics_items.Edge]:

        return None #Moved to tool.Edge

    @classmethod
    def find_ifc_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], graphics_items.Edge]],
        bsdd_dictionary: BsddDictionary,
    ):
        return None #Moved to tool.Edge


    @classmethod
    def find_class_property_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: RelationsDict,
        bsdd_dictionary: BsddDictionary,
    ) -> list[graphics_items.Edge]:


        return None # Moved to tool.Edge

    @classmethod
    def find_property_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], graphics_items.Edge]],
        bsdd_dictionary: BsddDictionary,
    ) -> list[graphics_items.Edge]:
        return None # Moved to tool.Edge

    @classmethod
    def insert_properties_in_scene(
        cls,
        bsdd_dictionary: BsddDictionary,
        scene: view_ui.GraphScene,
        bsdd_properties: list[BsddProperty],
        position: QPointF = None,
    ):
        return None #core.SceneView

    @classmethod
    def get_settings_widget(cls) -> ui_settings_widget.SettingsSidebar:
        widget = cls.get_widget()
        if not widget:
            return None
        return widget.settings_sidebar

    # --- Import/Export ----------------------------------------------------
    @classmethod
    def _collect_layout(cls) -> dict:
        return #Moved to Node

    @classmethod
    def clear_scene(cls):
        return None# Split into core.Edge and core.Node with Signal from Scene.clear_scene_requested
   
    @classmethod
    def center_scene(cls):
        return None # Moved to core.SceneView
    
    @classmethod
    def retranslate_buttons(cls):
        return None #Moved to core.SceneView

    @classmethod
    def toggle_running(cls):
        return None# Moved to Phyiscs

    @classmethod
    def pause(cls):
        return None# Moved to Phyiscs


    @classmethod
    def play(cls):
        return None# Moved to Phyiscs

    @classmethod
    def get_selected_items(cls) -> tuple[list[graphics_items.Node], list[graphics_items.Edge]]:

        return None #Moved to tool.SceneView

    @classmethod
    def remove_edge(
        cls,
        edge: graphics_items.Edge,
        bsdd_dictionary: BsddDictionary,
        only_visual=False,
        allow_parent_deletion=False,
    ):
        return None #Moved to tool.Edge

    @classmethod
    def remove_node(
        cls,
        node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
        ignored_edges: list[graphics_items.Edge] = None,
    ):
       return None # Moved to tool.Node

    @classmethod
    def import_node_from_json(
        cls, item: dict, bsdd_dictionary: BsddDictionary, ifc_classes, external_nodes
    ):
        return None # Moved to Node
    
    @classmethod
    def get_node_from_bsdd_data(
        cls, bsdd_data: BsddClass | BsddProperty
    ) -> graphics_items.Node | None:
        return None#Moved to tool.Node

    @classmethod
    def get_node_from_ifc_code(cls, ifc_code: str):
        return None#Moved to tool.Node

    @classmethod
    def read_relation(
        cls, relation: BsddClassRelation | BsddPropertyRelation, bsdd_dictionary: BsddDictionary
    ):
        return None#Moved to tool.Edge

    @classmethod
    def get_connected_edges(cls, node: graphics_items.Node) -> set[graphics_items.Edge]:
        return None#Moved to tool.Edge


    @classmethod
    def get_edge_from_nodes(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node | str,
        edge_type: str,
    ) -> graphics_items.Edge | None:
        return None#Moved to tool.Edge

    @classmethod
    def get_edge_from_relation(
        cls, relation: BsddClassRelation | BsddPropertyRelation, bsdd_dictionary: BsddDictionary
    ):
        return None#Moved to tool.Edge
    
    @classmethod
    def get_relation_from_edge(cls, edge: graphics_items.Edge, bsdd_dictionary: BsddDictionary):
        return None#Moved to tool.Edge


    @classmethod
    def update_add_completer(cls, bsdd_dictionary: BsddDictionary):
        return None #Moved to InputBar

    ### BUchheim

    @classmethod
    def find_roots(cls) -> list[graphics_items.Node]:
        sc = cls.get_scene()
        roots = list()
        for node in sc.nodes:
            if cls.parent(node) is None:
                roots.append(node)
        return roots

    @classmethod
    def intialize(cls, v: graphics_items.Node, depth=0, number: int = 1):
        v.thread = None
        v._lmost_sibling = None
        v.mod = 0
        v.change = 0
        v.shift = 0
        v.ancestor = v
        v.number = None
        cls.get_properties().position_dict[v] = [-1.0, depth]
        v.number = number
        for index, w in enumerate(cls.children(v)):
            cls.intialize(w, depth + 1, index + 1)

    @classmethod
    def buchheim(cls, v: view_ui.Node):
        tree = cls.firstwalk(v, 0)
        cls.second_walk(tree)
        return tree

    @classmethod
    def reset_children_dict(cls):
        sc = cls.get_scene()
        children_dict = dict()  # list all children
        parent_dict = {node: None for node in sc.nodes}
        edge_type = cls.get_widget().get_active_edge_type()
        if edge_type not in constants.ALLOWED_EDGE_TYPES:
            return False
        for edge in sc.edges:
            if edge.edge_type != edge_type:
                continue
            start_node = edge.start_node
            end_node = edge.end_node
            parent_dict[start_node] = end_node
            if end_node not in children_dict:
                children_dict[end_node] = list()
            children_dict[end_node].append(start_node)
        cls.get_properties().children_dict = children_dict
        cls.get_properties().parent_dict = parent_dict
        return True
        return True

    @classmethod
    def firstwalk(cls, v: view_ui.Node, depth):
        while depth >= len(cls.get_properties().height_list):
            cls.get_properties().height_list.append(0.0)
        cls.get_properties().height_list[depth] = max(
            cls.get_properties().height_list[depth], cls.height(v)
        )

        if len(cls.children(v)) == 0:  # no children exist
            # If a left brother exists, place next to it; otherwise start at 0
            lbrother = cls.lbrother(v)
            if lbrother:
                sibling_sep = (cls.width(lbrother) + cls.width(v)) / 2.0 + constants.X_MARGIN
                cls.set_x(v, cls.x(lbrother) + sibling_sep)
            else:
                cls.set_x(v, 0.0)

        else:
            default_ancestor = cls.children(v)[0]  # elektrotechnik
            for w in cls.children(v):
                cls.firstwalk(w, depth + 1)
                default_ancestor = cls.apportion(w, default_ancestor)
            c1 = cls.x(cls.children(v)[0])
            c2 = cls.x(cls.children(v)[-1])
            midpoint = (c1 + c2) / 2

            w = cls.lbrother(v)
            if w:
                # Align current subtree next to its left brother with symmetric spacing
                sibling_sep = (cls.width(w) + cls.width(v)) / 2.0 + constants.X_MARGIN
                new_x = cls.x(w) + sibling_sep
                cls.set_x(v, new_x)
                v.mod = new_x - midpoint
            else:
                cls.set_x(v, midpoint)
        return v

    @classmethod
    def second_walk(cls, v: view_ui.Node, m=0, depth=0):
        cls.set_x(v, cls.x(v) + m)
        height_list = cls.get_properties().height_list
        cls.set_y(v, sum(height_list[:depth]) + constants.Y_MARGIN * depth)
        for w in cls.children(v):
            cls.second_walk(w, m + v.mod, depth + 1)

    @classmethod
    def apportion(cls, v: view_ui.Node, default_ancestor: view_ui.Node):
        w = cls.lbrother(v)
        if w is None:
            return default_ancestor
        # in buchheim notation:
        # i == inner; o == outer; r == right; l == left; r = +; l = -
        vir = vor = v
        vil = w
        vol = cls.get_lmost_sibling(v)
        sir = sor = v.mod
        sil = vil.mod
        sol = vol.mod
        while cls.right(vil) and cls.left(vir):
            vil = cls.right(vil)
            vir = cls.left(vir)
            vol = cls.left(vol)
            vor = cls.right(vor)
            vor.ancestor = v
            # Use both nodes' half-widths to avoid overlap and enforce a symmetric margin
            sep = (cls.width(vil) + cls.width(vir)) / 2.0 + constants.X_MARGIN * 2
            shift = (cls.x(vil) + sil) - (cls.x(vir) + sir) + sep
            if shift > 0:
                cls.move_subtree(cls.ancestor(vil, v, default_ancestor), v, shift)
                sir = sir + shift
                sor = sor + shift
            sil += vil.mod
            sir += vir.mod
            sol += vol.mod
            sor += vor.mod
        if cls.right(vil) and not cls.right(vor):
            vor.thread = cls.right(vil)
            vor.mod += sil - sor
        if cls.left(vir) and not cls.left(vol):
            vol.thread = cls.left(vir)
            vol.mod += sir - sol
            default_ancestor = v
        return default_ancestor

    @classmethod
    def move_subtree(cls, wl: view_ui.Node, wr: view_ui.Node, shift: float):
        subtrees = (wr.number or 0) - (wl.number or 0)
        if subtrees <= 0:
            subtrees = 1
        wr.change -= shift / subtrees
        wr.shift += shift
        wl.change += shift / subtrees
        cls.set_x(wr, cls.x(wr) + shift)
        wr.mod += shift

    @classmethod
    def ancestor(
        cls,
        vil: view_ui.Node,
        v: view_ui.Node,
        default_ancestor: view_ui.Node,
    ):
        pv = cls.parent(v)
        siblings = cls.children(pv) if pv else []
        if vil.ancestor in siblings:
            return vil.ancestor
        else:
            return default_ancestor

    @classmethod
    def rearrange(cls, root_node: view_ui.Node, base_pos: QPointF):
        def ra(v: view_ui.Node):
            x, y = cls.pos(v)
            x = base_pos.x() + x
            y = base_pos.y() + y
            v.setPos(QPointF(x, y))
            for child in cls.children(v):
                ra(child)

        ra(root_node)

    # NodeProxy getter functions

    @classmethod
    def children(cls, v: view_ui.Node) -> list[view_ui.Node]:
        # Preserve original insertion order from children_dict; sorting by x corrupts numbering
        return cls.get_properties().children_dict.get(v, [])

    @classmethod
    def parent(cls, v: view_ui.Node) -> view_ui.Node:
        return cls.get_properties().parent_dict.get(v)

    @classmethod
    def left(cls, v: view_ui.Node):
        if v.thread:
            return v.thread
        ch = cls.children(v)
        return ch[0] if ch else None

    @classmethod
    def right(cls, v: view_ui.Node):
        if v.thread:
            return v.thread
        ch = cls.children(v)
        return ch[-1] if ch else None

    @classmethod
    def lbrother(cls, v: view_ui.Node):
        n = None
        parent = cls.parent(v)
        if parent:
            for node in cls.children(parent):
                if node == v:
                    return n
                else:
                    n = node
        return n

    @classmethod
    def get_lmost_sibling(cls, v: view_ui.Node) -> view_ui.Node:
        p = cls.parent(v)
        if not p:
            return v
        ch = cls.children(p)
        if not ch:
            return v
        first = ch[0]
        if v._lmost_sibling is None:
            v._lmost_sibling = first
        return v if v == first else v._lmost_sibling

    @classmethod
    def x(cls, v: view_ui.Node):
        return cls.get_properties().position_dict[v][0]

    @classmethod
    def y(cls, v: view_ui.Node):
        return cls.get_properties().position_dict[v][1]

    @classmethod
    def set_x(cls, v: view_ui.Node, x: float):
        cls.get_properties().position_dict[v][0] = x

    @classmethod
    def set_y(cls, v: view_ui.Node, y: float):
        cls.get_properties().position_dict[v][1] = y

    @classmethod
    def pos(cls, v: view_ui.Node):
        return cls.get_properties().position_dict[v]

    @classmethod
    def width(cls, v: view_ui.Node):
        return getattr(v, "_w", 24.0)

    @classmethod
    def height(cls, v: view_ui.Node):
        return getattr(v, "_h", 24.0)
