from __future__ import annotations
from typing import TYPE_CHECKING, Optional, TypedDict
import logging

from PySide6.QtGui import QDropEvent, QColor
from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtCore import QPointF, QCoreApplication, QRectF, Qt
import json

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, WidgetTool
from bsdd_gui.presets.signal_presets import WidgetSignals
from PySide6.QtCore import Signal

import random
from bsdd_gui.module.ifc_helper.data import IfcHelperData

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.prop import GraphViewWidgetProperties
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

from bsdd_gui.module.graph_view_widget import (
    trigger,
    ui,
    constants,
    ui_settings_widget,
    graphics_items,
    view_ui,
)
from bsdd_gui.module.graph_view_widget.graphics_items import Node
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import JSON_MIME as PROPERTY_JSON_MIME


class InfoDict(TypedDict):
    start_uri: str
    end_uri: str
    start_node_type: str
    end_node_type: str


RelationsDict = dict[
    constants.ALLOWED_EDGE_TYPES_TYPING, dict[tuple[str, str, str, str], graphics_items.Edge]
]


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
        from bsdd_gui.module.graph_view_widget.ui import GraphWindow

        return GraphWindow

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.node_double_clicked.connect(trigger.node_double_clicked)

    @classmethod
    def connect_widget_signals(cls, widget: ui.GraphWindow):
        settings_sidebar = widget.settings_sidebar
        bs = settings_sidebar._button_settings
        bs.bt_load.clicked.connect(lambda _: trigger.load_bsdd())
        bs.bt_start_stop.clicked.connect(lambda _: cls.toggle_running())
        bs.bt_clear.clicked.connect(lambda _: cls.clear_scene())
        bs.bt_center.clicked.connect(lambda _: cls.center_scene())
        # Import/Export current graph layout (nodes + positions)
        bs.bt_export.clicked.connect(lambda _: trigger.export_requested())
        bs.bt_import.clicked.connect(lambda _: trigger.import_requested())
        bs.bt_tree.clicked.connect(lambda _: trigger.buchheim())

    @classmethod
    def create_widget(cls, *args, **kwargs):
        widget: ui.GraphWindow = super().create_widget(*args, **kwargs)
        return widget

    @classmethod
    def populate_from_bsdd(cls, widget: ui.GraphWindow, bsdd_dict: BsddDictionary):
        # Build graph from bSDD model: Classes and Properties
        # Node registries
        class_by_code: dict[str, Node] = {}
        class_by_uri: dict[str, Node] = {}
        prop_by_code: dict[str, Node] = {}
        prop_by_uri: dict[str, Node] = {}

        # 1) Classes
        scene = widget.scene
        for c in bsdd_dict.Classes:
            n = cls.add_node(scene, c)
            class_by_code[c.Code] = n
            try:
                uri = cl_utils.build_bsdd_uri(c, bsdd_dict)
                if uri:
                    class_by_uri[uri] = n
            except Exception:
                pass

        # 2) Properties (dictionary-level)
        for p in bsdd_dict.Properties:
            n = cls.add_node(scene, p)
            prop_by_code[p.Code] = n
            # Map canonical bsDD URI and any owned URI
            try:
                uri = prop_utils.build_bsdd_uri(p, bsdd_dict)
                if uri:
                    prop_by_uri[uri] = n
            except Exception:
                pass
            if getattr(p, "OwnedUri", None):
                prop_by_uri[p.OwnedUri] = n

        # 3) Class → Property edges via ClassProperties
        for c in bsdd_dict.Classes:
            cnode = class_by_code.get(c.Code)
            if not cnode:
                continue
            for cp in c.ClassProperties:
                target_node = None
                # Prefer PropertyUri mapping
                if getattr(cp, "PropertyUri", None):
                    target_node = prop_by_uri.get(cp.PropertyUri)
                    if target_node is None:
                        # try parse to code
                        try:
                            parsed = dict_utils.parse_bsdd_url(cp.PropertyUri)
                            code = parsed.get("resource_id")
                            if code:
                                target_node = prop_by_code.get(code)
                        except Exception:
                            pass
                # Fallback to PropertyCode
                if target_node is None and getattr(cp, "PropertyCode", None):
                    target_node = prop_by_code.get(cp.PropertyCode)
                if target_node is not None:
                    edge = cls.create_edge(
                        cnode, target_node, weight=1.0, edge_type=constants.C_P_REL
                    )
                    cls.add_edge(scene, edge)

        # 4) ClassRelations edges (Class -> Class)
        for c in bsdd_dict.Classes:
            src_node = class_by_code.get(c.Code)
            if not src_node:
                continue
            dst_node = class_by_code.get(c.ParentClassCode)
            if not dst_node:
                continue
            edge = cls.create_edge(src_node, dst_node, weight=1.0, edge_type="class_rel")
            cls.add_edge(scene, edge)
            # for rel in c.ClassRelations:
            #     dst_node = class_by_uri.get(rel.RelatedClassUri)
            #     if dst_node is not None:
            #         scene.scene.add_edge(
            #             src_node, dst_node, weight=1.0, edge_type="class_rel"
            #         )

        # 5) PropertyRelations edges (Property -> Property)
        for p in bsdd_dict.Properties:
            src_node = prop_by_code.get(p.Code)
            if not src_node:
                continue
            for rel in p.PropertyRelations:
                dst = prop_by_uri.get(rel.RelatedPropertyUri)
                if dst is None:
                    # Fallback: parse URI to code
                    try:
                        parsed = dict_utils.parse_bsdd_url(rel.RelatedPropertyUri)
                        code = parsed.get("resource_id")
                        if code and code in prop_by_code:
                            dst = prop_by_code[code]
                    except Exception:
                        pass
                if dst is not None:
                    edge = cls.create_edge(src_node, dst, weight=0.0, edge_type="prop_rel")
                    cls.add_edge(scene, edge)

        # No ClassProperty nodes are created; edges Class→Property were added above.

        # Apply current filters to the newly created graph
        widget._apply_filters()

    @classmethod
    def get_widget(cls) -> ui.GraphWindow:
        if not cls.get_widgets():
            return None
        return cls.get_widgets()[-1]

    ### Drag and Drop

    @classmethod
    def get_mime_type(cls, mime_data) -> constants.ALLOWED_DRAG_TYPES | None:
        if mime_data.hasFormat(PROPERTY_JSON_MIME):
            return constants.PROPERTY_DRAG
        if mime_data.hasFormat(CLASS_JSON_MIME):
            return constants.CLASS_DRAG
        return None

    @classmethod
    def get_position_from_event(cls, event: QDropEvent, gv: view_ui):
        try:
            pos_view = event.position()
            # mapToScene expects int coordinates
            scene_pos = gv.mapToScene(int(pos_view.x()), int(pos_view.y()))
        except Exception:
            scene_pos = gv.mapToScene(event.pos())
        return scene_pos

    @classmethod
    def read_classes_to_add(cls, payload: dict, bsdd_dictionary: BsddDictionary):
        classes_to_add = list()
        if not "classes" in payload:
            return []
        for rc in payload["classes"]:
            code = rc.get("Code", None)
            if not code:
                continue
            bsdd_class = cl_utils.get_class_by_code(bsdd_dictionary, code)
            if not bsdd_class:
                continue
            classes_to_add.append(bsdd_class)
        return classes_to_add

    @classmethod
    def read_properties_to_add(cls, payload: dict, bsdd_dictionary: BsddDictionary):
        properties_to_add = list()
        if not "properties" in payload:
            return []
        for rp in payload["properties"]:
            code = rp.get("Code")
            if not code:
                continue
            bsdd_property = prop_utils.get_property_by_code(code, bsdd_dictionary)
            if not bsdd_property:
                continue
            properties_to_add.append(bsdd_property)
        return properties_to_add

    @classmethod
    def create_edge(
        cls,
        start_node: Node,
        end_node: Node,
        edge_type,
        weight: float = 1.0,
    ):
        return graphics_items.Edge(start_node, end_node, edge_type, weight)

    @classmethod
    def add_edge(
        cls,
        scene: view_ui.GraphScene,
        edge: graphics_items.Edge,
    ) -> graphics_items.Edge:

        for existing_edge in scene.edges:
            if existing_edge.start_node.bsdd_data != edge.start_node.bsdd_data:
                continue
            if existing_edge.end_node.bsdd_data != edge.end_node.bsdd_data:
                continue
            if existing_edge.edge_type == edge.edge_type:
                logging.info(f"Edge allread exists {edge}")
                return None
        scene.addItem(edge)
        scene.edges.append(edge)
        return edge

    @classmethod
    def add_node(
        cls,
        scene: view_ui.GraphScene,
        bsdd_data: BsddClass | BsddProperty,
        pos: Optional[QPointF] = None,
        color: Optional[QColor] = None,
        is_external=False,
    ) -> Node:

        n = Node(bsdd_data, color=color, is_external=is_external)
        p = (
            pos
            if pos is not None
            else QPointF(random.uniform(-150, 150), random.uniform(-150, 150))
        )
        n.setPos(p)
        scene.addItem(n)
        scene.nodes.append(n)
        return n

    @classmethod
    def insert_classes_in_scene(
        cls,
        bsdd_dictionary: BsddDictionary,
        scene: view_ui.GraphScene,
        classes: list[BsddClass],
        position: QPointF = None,
        ifc_classes: dict[str, dict[str, str]] = dict(),
    ):
        if position is None:
            position = QPointF(scene.sceneRect().width() / 2, scene.sceneRect().height() / 2)
        offset_step = QPointF(24.0, 18.0)
        cur = QPointF(position)
        new_nodes = list()

        existing_nodes = {n for n in scene.nodes if hasattr(n, "bsdd_data")}
        external_nodes = {n.bsdd_data.OwnedUri: n for n in existing_nodes if n.is_external}
        internal_nodes = {
            cl_utils.build_bsdd_uri(n.bsdd_data, bsdd_dictionary): n
            for n in existing_nodes
            if n.node_type == constants.CLASS_NODE_TYPE
        }

        for bsdd_class in classes:
            class_uri = cl_utils.build_bsdd_uri(bsdd_class, bsdd_dictionary)
            if class_uri not in internal_nodes:
                new_node = cls.add_node(scene, bsdd_class, pos=cur, is_external=False)
                new_nodes.append(new_node)
                internal_nodes[class_uri] = new_node
                cur += offset_step

            ifc_entities = bsdd_class.RelatedIfcEntityNamesList or []
            for e in ifc_entities:
                new_node = cls.add_ifc_node(e, cur, ifc_classes, external_nodes)
                if new_node:
                    cur += offset_step
                    temp_bsdd_class = new_node.bsdd_data
                    external_nodes[temp_bsdd_class.OwnedUri] = temp_bsdd_class

            for class_relation in bsdd_class.ClassRelations:
                related_uri = class_relation.RelatedClassUri
                if related_uri in external_nodes:
                    continue
                if related_uri in internal_nodes:
                    continue
                related_bsdd_class = cl_utils.get_class_by_uri(bsdd_dictionary, related_uri)
                if related_bsdd_class.OwnedUri and cl_utils.is_external_ref(
                    related_bsdd_class.OwnedUri, bsdd_dictionary
                ):
                    new_node = cls.add_node(scene, related_bsdd_class, pos=cur, is_external=True)
                    external_nodes[related_bsdd_class.OwnedUri] = new_node.bsdd_data

                else:
                    new_node = cls.add_node(scene, related_bsdd_class, pos=cur, is_external=False)
                    internal_nodes[cl_utils.build_bsdd_uri(related_bsdd_class, bsdd_dictionary)] = (
                        new_node.bsdd_data
                    )
                new_nodes.append(new_node)
                cur += offset_step
        return new_nodes

    @classmethod
    def add_ifc_node(
        cls, ifc_code: str, position: QPointF, ifc_classes: dict = None, external_nodes=None
    ):
        scene = cls.get_scene()
        if not ifc_classes:
            ifc_classes = {c.get("code"): c for c in IfcHelperData.get_classes()}
        if not external_nodes:
            existing_nodes = {
                n
                for n in scene.nodes
                if hasattr(n, "bsdd_data") and n.node_type == constants.CLASS_NODE_TYPE
            }
            external_nodes = {n.bsdd_data.OwnedUri: n for n in existing_nodes if n.is_external}

        ifc_class_dict = ifc_classes.get(ifc_code)
        if not ifc_class_dict:
            return
        uri = ifc_class_dict.get("uri")
        if uri in external_nodes:
            return
        ifc_class = BsddClass(
            Code=ifc_code,
            Name=ifc_class_dict.get("referenceCode"),
            ClassType=ifc_class_dict.get("classType"),
            OwnedUri=uri,
        )
        new_node = cls.add_node(scene, ifc_class, pos=position, is_external=True)
        return new_node

    @classmethod
    def get_uri_from_node(cls, node: Node, bsdd_dictionary: BsddDictionary):
        if node.node_type in [
            constants.EXTERNAL_CLASS_NODE_TYPE,
            constants.EXTERNAL_PROPERTY_NODE_TYPE,
            constants.IFC_NODE_TYPE,
        ]:
            uri = node.bsdd_data.OwnedUri
        elif node.node_type == constants.CLASS_NODE_TYPE:
            uri = cl_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
        elif node.node_type == constants.PROPERTY_NODE_TYPE:
            uri = prop_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
        else:
            uri = None
        return uri

    @classmethod
    def _info(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
    ):
        d = [None, None, None, None]
        d[0] = start_node.node_type
        d[1] = cls.get_uri_from_node(start_node, bsdd_dictionary)
        if end_node:
            d[2] = end_node.node_type
            d[3] = cls.get_uri_from_node(end_node, bsdd_dictionary)
        return tuple(d)

    @classmethod
    def get_code_dicts(cls, scene: view_ui.GraphScene, bsdd_dictionary: BsddDictionary):
        nodes = scene.nodes
        edges = scene.edges

        uri_dict = dict()

        for node in nodes:
            if node.node_type == constants.CLASS_NODE_TYPE:
                uri = cl_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
            elif node.node_type == constants.EXTERNAL_CLASS_NODE_TYPE:
                uri = node.bsdd_data.OwnedUri
            elif node.node_type == constants.PROPERTY_NODE_TYPE:
                uri = prop_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
            elif node.node_type == constants.EXTERNAL_PROPERTY_NODE_TYPE:
                uri = node.bsdd_data.OwnedUri
            elif node.node_type == constants.IFC_NODE_TYPE:
                uri = node.bsdd_data.OwnedUri
            else:
                logging.warning(f"Unknown node type for uri extraction: {node.node_type}")
                continue
            uri_dict[uri] = node

        relations_dict: RelationsDict = {et: dict() for et in constants.ALLOWED_EDGE_TYPES}
        for edge in edges:
            info = cls._info(edge.start_node, edge.end_node, bsdd_dictionary)
            if info in relations_dict[edge.edge_type]:
                logging.info(f"Relationship duplicate found")
            relations_dict[edge.edge_type][info] = edge
        return uri_dict, relations_dict

    @classmethod
    def find_class_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], graphics_items.Edge]],
        bsdd_dictionary: BsddDictionary,
    ) -> list[graphics_items.Edge]:
        new_edges = list()
        for start_node in nodes:
            if start_node.node_type != constants.CLASS_NODE_TYPE:
                continue
            start_class = start_node.bsdd_data
            parent_class = cl_utils.get_class_by_code(bsdd_dictionary, start_class.ParentClassCode)
            if parent_class:
                parent_uri = cl_utils.build_bsdd_uri(parent_class, bsdd_dictionary)
                related_node = uri_dict.get(parent_uri)
                relation_type = constants.PARENT_CLASS
                info = cls._info(start_node, related_node, bsdd_dictionary)

            if related_node is not None and info not in existing_relations_dict[relation_type]:
                edge = cls.create_edge(start_node, related_node, edge_type=constants.PARENT_CLASS)
                new_edges.append(edge)
                existing_relations_dict[relation_type][info] = edge

            for relation in start_class.ClassRelations:
                related_node = uri_dict.get(relation.RelatedClassUri)
                if related_node is None:
                    continue
                info = cls._info(start_node, related_node, bsdd_dictionary)
                relation_type = relation.RelationType
                if related_node is not None and info not in existing_relations_dict[relation_type]:
                    edge = cls.create_edge(start_node, related_node, edge_type=relation_type)
                    new_edges.append(edge)
                    existing_relations_dict[relation_type][info] = edge
        return new_edges

    @classmethod
    def find_ifc_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], graphics_items.Edge]],
        bsdd_dictionary: BsddDictionary,
    ):
        ifc_dict = {c["code"]: c for c in IfcHelperData.get_classes()}
        new_edges = list()
        relation_type = constants.IFC_REFERENCE_REL
        for start_node in nodes:
            if start_node.node_type != constants.CLASS_NODE_TYPE or start_node.is_external:
                continue
            start_class = start_node.bsdd_data
            for ifc_name in start_class.RelatedIfcEntityNamesList or []:
                ifc_uri = ifc_dict.get(ifc_name).get("uri")
                related_node = uri_dict.get(ifc_uri)
                if not related_node:
                    continue
                info = cls._info(start_node, related_node, bsdd_dictionary)
                if related_node is not None and info not in existing_relations_dict[relation_type]:
                    edge = cls.create_edge(start_node, related_node, edge_type=relation_type)
                    new_edges.append(edge)
                    existing_relations_dict[relation_type][info] = edge
        return new_edges

    @classmethod
    def find_class_property_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: RelationsDict,
        bsdd_dictionary: BsddDictionary,
    ) -> list[graphics_items.Edge]:

        new_edges = list()
        for start_node in nodes:
            if start_node.node_type != constants.CLASS_NODE_TYPE:
                continue
            start_class = start_node.bsdd_data
            for cp in start_class.ClassProperties:
                if cp.PropertyUri:
                    related_node = uri_dict.get(cp.PropertyUri)
                else:
                    bsdd_property = prop_utils.get_property_by_class_property(cp, bsdd_dictionary)
                    related_node = uri_dict.get(
                        prop_utils.build_bsdd_uri(bsdd_property, bsdd_dictionary)
                    )
                if related_node is None:
                    continue
                info = cls._info(start_node, related_node, bsdd_dictionary)
                relation_type = constants.C_P_REL
                if info not in existing_relations_dict[relation_type]:
                    edge = cls.create_edge(start_node, related_node, edge_type=relation_type)
                    new_edges.append(edge)
                    existing_relations_dict[relation_type][info] = edge
        return new_edges

    @classmethod
    def find_property_relations(
        cls,
        nodes: list[graphics_items.Node],
        uri_dict: dict[str, graphics_items.Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], graphics_items.Edge]],
        bsdd_dictionary: BsddDictionary,
    ) -> list[graphics_items.Edge]:
        new_edges = list()
        for start_node in nodes:
            if start_node.node_type != constants.PROPERTY_NODE_TYPE:
                continue
            start_property = start_node.bsdd_data
            for relation in start_property.PropertyRelations:
                related_node = uri_dict.get(relation.RelatedPropertyUri)
                if related_node is None:
                    continue
                info = cls._info(start_node, related_node, bsdd_dictionary)
                relation_type = relation.RelationType
                if related_node is not None and info not in existing_relations_dict[relation_type]:
                    edge = cls.create_edge(start_node, related_node, edge_type=relation_type)
                    new_edges.append(edge)
                    existing_relations_dict[relation_type][info] = edge
        return new_edges

    @classmethod
    def insert_properties_in_scene(
        cls,
        bsdd_dictionary: BsddDictionary,
        scene: view_ui.GraphScene,
        bsdd_properties: list[BsddProperty],
        position: QPointF = None,
    ):
        if position is None:
            position = QPointF(scene.sceneRect().width() / 2, scene.sceneRect().height() / 2)
        offset_step = QPointF(24.0, 18.0)
        cur = QPointF(position)

        new_nodes = list()
        existing_nodes = {n for n in scene.nodes if hasattr(n, "bsdd_data")}
        external_nodes = {n.bsdd_data.OwnedUri: n for n in existing_nodes if n.is_external}
        internal_nodes = {
            prop_utils.build_bsdd_uri(n.bsdd_data, bsdd_dictionary): n
            for n in existing_nodes
            if n.node_type == constants.PROPERTY_NODE_TYPE
        }
        for bsdd_property in bsdd_properties:
            prop_uri = prop_utils.build_bsdd_uri(bsdd_property, bsdd_dictionary)
            if prop_uri not in internal_nodes:
                new_node = cls.add_node(scene, bsdd_property, pos=cur, is_external=False)
                new_nodes.append(new_node)
                internal_nodes[prop_uri] = new_node
                cur += offset_step

            for property_relation in bsdd_property.PropertyRelations:
                related_uri = property_relation.RelatedPropertyUri
                if related_uri in external_nodes:
                    continue
                if related_uri in internal_nodes:
                    continue
                related_bsdd_property = prop_utils.get_property_by_uri(related_uri, bsdd_dictionary)
                if related_bsdd_property.OwnedUri and dict_utils.is_external_ref(
                    related_bsdd_property.OwnedUri, bsdd_dictionary
                ):
                    new_node = cls.add_node(scene, related_bsdd_property, pos=cur, is_external=True)
                    external_nodes[related_bsdd_property.OwnedUri] = new_node.bsdd_data
                else:
                    new_node = cls.add_node(
                        scene, related_bsdd_property, pos=cur, is_external=False
                    )
                    internal_nodes[
                        cl_utils.build_bsdd_uri(related_bsdd_property, bsdd_dictionary)
                    ] = new_node.bsdd_data
                new_nodes.append(new_node)
                cur += offset_step
        return new_nodes

    @classmethod
    def get_view(cls) -> view_ui.GraphView:
        widget: ui.GraphWindow = cls.get_widget()
        if not widget:
            return None
        return widget.view

    @classmethod
    def get_scene(cls) -> view_ui.GraphScene | None:
        view: view_ui.GraphView = cls.get_view()
        if not view:
            return None
        return view.scene()

    @classmethod
    def get_settings_widget(cls) -> ui_settings_widget.SettingsSidebar:
        widget = cls.get_widget()
        if not widget:
            return None
        return widget.settings_sidebar

    # --- Import/Export ----------------------------------------------------
    @classmethod
    def _collect_layout(cls) -> dict:
        scene = cls.get_scene()
        if scene is None:
            return {"version": 1, "nodes": []}
        nodes_payload = []
        for n in scene.nodes:
            try:
                code = getattr(n.bsdd_data, "Code", None)
                if code is None:
                    continue
                p = n.pos()
                nodes_payload.append(
                    {
                        "type": getattr(n, "node_type", None),
                        "code": code,
                        "pos": [float(p.x()), float(p.y())],
                    }
                )
            except Exception:
                continue
        return {"version": 1, "nodes": nodes_payload}

    @classmethod
    def clear_scene(cls):
        scene = cls.get_scene()
        if scene is None:
            return
        for e in scene.edges:
            scene.removeItem(e)
        for n in scene.nodes:
            scene.removeItem(n)
        scene.nodes.clear()
        scene.edges.clear()

    @classmethod
    def center_scene(cls):
        scene = cls.get_scene()
        view = cls.get_view()
        if scene is None:
            return
        # Fit to visible nodes if any, with a small buffer
        vis = [n for n in scene.nodes if n.isVisible()]
        items = vis if vis else scene.nodes
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

    @classmethod
    def retranslate_buttons(cls):
        scene = cls.get_scene()
        if not scene:
            return
        button_widget = cls.get_settings_widget()._button_settings
        button_widget.retranslateUi(button_widget)
        pause_text = QCoreApplication.translate("GraphView", "Pause")
        play_text = QCoreApplication.translate("GraphView", "Play")
        button_widget.bt_start_stop.setText(pause_text if scene.running else play_text)

    @classmethod
    def toggle_running(cls):
        scene = cls.get_scene()
        scene.running = not scene.running
        cls.retranslate_buttons()

    @classmethod
    def pause(cls):
        scene = cls.get_scene()
        if not scene:
            return
        scene.running = False

    @classmethod
    def play(cls):
        scene = cls.get_scene()
        if not scene:
            return
        scene.running = True

    @classmethod
    def create_class_property_relation(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
    ):
        bsdd_class = (
            start_node.bsdd_data
            if start_node.node_type == constants.CLASS_NODE_TYPE
            else end_node.bsdd_data
        )
        bsdd_property = (
            start_node.bsdd_data
            if start_node.node_type == constants.PROPERTY_NODE_TYPE
            else end_node.bsdd_data
        )

        # check if relationship exists allready
        for bsdd_class_property in bsdd_class.ClassProperties:
            if bsdd_property == prop_utils.get_internal_property(
                bsdd_class_property, bsdd_dictionary
            ):
                return

        new_property = prop_utils.create_class_property_from_internal_property(
            bsdd_property, bsdd_class
        )
        new_property._set_parent(bsdd_class)
        bsdd_class.ClassProperties.append(new_property)
        cls.signals.new_class_property_created.emit(new_property)
        new_edge = cls.create_edge(start_node, end_node, edge_type=constants.C_P_REL)
        cls.add_edge(cls.get_scene(), new_edge)

    @classmethod
    def create_class_class_relation(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
        relation: constants.ALLOWED_EDGE_TYPES_TYPING,
    ):
        start_class: BsddClass = start_node.bsdd_data
        end_class: BsddClass = end_node.bsdd_data

        if relation not in constants.CLASS_RELATIONS:
            return
        if relation == constants.IFC_REFERENCE_REL:
            if not isinstance(end_class, constants.IFC_NODE_TYPE):
                return
            rienl = [x.lower() for x in start_class.RelatedIfcEntityNamesList or []]
            if end_class.Code.lower() not in rienl:
                start_class.RelatedIfcEntityNamesList.append(end_class.Code)

        else:
            if end_class.OwnedUri:
                end_uri = end_class.OwnedUri
            else:
                end_uri = cl_utils.build_bsdd_uri(end_class, bsdd_dictionary)
            existing_relations = [
                r.RelationType for r in start_class.ClassRelations if r.RelatedClassUri == end_uri
            ]
            if relation in existing_relations:
                return
            new_relation = BsddClassRelation(
                RelationType=relation, RelatedClassUri=end_uri, RelatedClassName=end_class.Name
            )
            new_relation._set_parent(start_class)
            start_class.ClassRelations.append(new_relation)
        new_edge = cls.create_edge(start_node, end_node, edge_type=relation)
        cls.add_edge(cls.get_scene(), new_edge)
        cls.signals.new_edge_created.emit(new_edge)

    @classmethod
    def create_property_property_relation(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
        relation: constants.ALLOWED_EDGE_TYPES_TYPING,
    ):
        start_property: BsddProperty = start_node.bsdd_data
        end_property: BsddProperty = end_node.bsdd_data

        if relation not in constants.PROPERTY_RELATIONS:
            return

        end_uri = prop_utils.build_bsdd_uri(end_property, bsdd_dictionary)
        existing_relations = [
            r.RelationType
            for r in start_property.PropertyRelations
            if r.RelatedPropertyUri == end_uri
        ]
        if relation in existing_relations:
            return
        new_relation = BsddPropertyRelation(
            RelationType=relation, RelatedPropertyUri=end_uri, RelatedPropertyName=end_property.Name
        )
        new_relation._set_parent(start_property)
        start_property.PropertyRelations.append(new_relation)
        new_edge = cls.create_edge(start_node, end_node, edge_type=relation)
        cls.add_edge(cls.get_scene(), new_edge)
        cls.signals.new_edge_created.emit(new_edge)

    @classmethod
    def get_selected_items(cls) -> tuple[list[graphics_items.Node], list[graphics_items.Edge]]:

        selected_nodes: list[graphics_items.Node] = []
        selected_edges: list[graphics_items.Edge] = []
        scene = cls.get_scene()
        if not scene:
            return [], []
        try:
            selected = list(scene.selectedItems())
        except Exception:
            selected = []
        if not selected:
            return [], []
        for it in selected:
            if isinstance(it, graphics_items.Node):
                selected_nodes.append(it)
            elif isinstance(it, graphics_items.Edge):
                selected_edges.append(it)
        return selected_nodes, selected_edges

    @classmethod
    def remove_edge(
        cls,
        edge: graphics_items.Edge,
        bsdd_dictionary: BsddDictionary,
        only_visual=False,
        allow_parent_deletion=False,
    ):
        """_summary_

        Args:
            edge (graphics_items.Edge): _description_
            only_visual (bool, optional): _description_. Delete edge only from scene but leave relationship intact
        """
        if edge is None:
            return
        scene = cls.get_scene()
        start_node, end_node = edge.start_node, edge.end_node
        relation_type = edge.edge_type
        if relation_type == constants.GENERIC_REL:
            return

        if relation_type == constants.PARENT_CLASS and not allow_parent_deletion:
            return

        if not scene:
            return
        try:
            scene.removeItem(edge)
        except Exception:
            pass
        try:
            if edge in scene.edges:
                scene.edges.remove(edge)
        except ValueError:
            pass
        if only_visual:
            return
        start_data, end_data = start_node.bsdd_data, end_node.bsdd_data

        if isinstance(start_data, BsddClass):
            if isinstance(end_data, BsddClass):
                if relation_type == constants.IFC_REFERENCE_REL:
                    start_data.RelatedIfcEntityNamesList.remove(end_data.Code)
                    cls.signals.ifc_reference_removed.emit(start_data, end_data.Code)
                else:
                    class_relation = cl_utils.get_class_relation(
                        start_data, end_data, relation_type
                    )
                    if not class_relation:
                        return
                    start_data.ClassRelations.remove(class_relation)
                    cls.signals.edge_removed.emit(edge)
                    cls.signals.class_relation_removed.emit(class_relation)
            elif isinstance(end_data, BsddProperty):
                class_property = {cp.PropertyCode: cp for cp in start_data.ClassProperties}.get(
                    end_data.Code
                )
                if class_property is None:
                    return
                start_data.ClassProperties.remove(class_property)
                cls.signals.class_property_removed.emit(class_property, start_data)
        elif isinstance(start_data, BsddProperty):
            if isinstance(end_data, BsddProperty):
                if end_node.is_external:
                    end_uri = end_data.OwnedUri
                else:
                    end_uri = prop_utils.build_bsdd_uri(end_data, bsdd_dictionary)
                property_relation = prop_utils.get_property_relation(
                    start_data, end_uri, relation_type
                )
                if not property_relation:
                    return
                start_data.PropertyRelations.remove(property_relation)
                cls.signals.property_relation_removed.emit(property_relation)

                cls.signals.edge_removed.emit(edge)
            elif isinstance(end_data, BsddClass):
                class_property = {cp.PropertyCode: cp for cp in end_data.ClassProperties}.get(
                    start_data.Code
                )
                if class_property is None:
                    return
                end_data.ClassProperties.remove(class_property)
                cls.signals.class_property_removed.emit(class_property, end_data)

    @classmethod
    def remove_node(
        cls,
        node: graphics_items.Node,
        bsdd_dictionary: BsddDictionary,
        ignored_edges: list[graphics_items.Edge] = None,
    ):
        ignored_edges = list() if ignored_edges is None else ignored_edges

        scene = cls.get_scene()
        if not scene:
            return
        for e in list(scene.edges):
            if e.edge_type != constants.PARENT_CLASS and e in ignored_edges:
                continue
            if e.start_node == node or e.end_node == node:
                cls.remove_edge(
                    e,
                    bsdd_dictionary,
                    bsdd_dictionary=bsdd_dictionary,
                    only_visual=True,
                    allow_parent_deletion=True,
                )

        try:
            scene.removeItem(node)
        except Exception:
            pass
        try:
            scene.nodes.remove(node)
        except ValueError:
            pass

    @classmethod
    def import_node_from_json(
        cls, item: dict, bsdd_dictionary: BsddDictionary, ifc_classes, external_nodes
    ):
        scene = cls.get_scene()
        try:
            ntype = item.get("type")
            code = item.get("code")
            pos = item.get("pos") or [0.0, 0.0]
            if not code or not ntype:
                return
            x, y = float(pos[0]), float(pos[1])
            bsdd_obj = None
            if bsdd_dictionary is not None:
                if ntype == constants.CLASS_NODE_TYPE:
                    bsdd_obj = cl_utils.get_class_by_code(bsdd_dictionary, code)
                elif ntype == constants.PROPERTY_NODE_TYPE:
                    bsdd_obj = prop_utils.get_property_by_code(code, bsdd_dictionary)
                elif ntype == constants.IFC_NODE_TYPE:
                    node = cls.add_ifc_node(code, QPointF(x, y), ifc_classes, external_nodes)
                    return node
            if bsdd_obj is None:
                return
            node = cls.add_node(scene, bsdd_obj, pos=QPointF(x, y))
            return node
        except Exception:
            return

    @classmethod
    def get_node_from_bsdd_data(
        cls, bsdd_data: BsddClass | BsddProperty
    ) -> graphics_items.Node | None:
        scene = cls.get_scene()
        if not scene:
            return None
        for node in scene.nodes:
            if node.bsdd_data == bsdd_data:
                return node
        return None

    @classmethod
    def get_node_from_ifc_code(cls, ifc_code: str):
        scene = cls.get_scene()
        if not scene:
            return None
        for node in scene.nodes:
            if node.is_external and node.bsdd_data.Code == ifc_code:
                return node

    @classmethod
    def read_relation(
        cls, relation: BsddClassRelation | BsddPropertyRelation, bsdd_dictionary: BsddDictionary
    ):
        start_data = relation._parent_ref()
        relation_type = relation.RelationType

        if isinstance(relation, BsddClassRelation):
            related_uri = relation.RelatedClassUri
            end_data = cl_utils.get_class_by_uri(bsdd_dictionary, related_uri)

        elif isinstance(relation, BsddPropertyRelation):
            related_uri = relation.RelatedPropertyUri
            code = dict_utils.parse_bsdd_url(related_uri).get("resource_id")
            end_data = prop_utils.get_property_by_code(code, bsdd_dictionary)
        return start_data, end_data, relation_type

    @classmethod
    def get_connected_edges(cls, node: graphics_items.Node) -> set[graphics_items.Edge]:
        scene = cls.get_scene()
        if not scene:
            return []
        connected_edges = set()
        for edge in scene.edges:
            if edge.start_node == node or edge.end_node == node:
                connected_edges.add(edge)
        return connected_edges

    @classmethod
    def get_edge_from_nodes(
        cls,
        start_node: graphics_items.Node,
        end_node: graphics_items.Node | str,
        edge_type: str,
    ) -> graphics_items.Edge | None:
        scene = cls.get_scene()
        if not scene:
            return None
        for edge in scene.edges:
            if edge.start_node.bsdd_data != start_node.bsdd_data:
                continue
            if edge_type == constants.IFC_REFERENCE_REL and isinstance(end_node, str):
                if not edge.end_node.is_external:
                    continue
                if edge.end_node.bsdd_data.Code == end_node:
                    continue
            elif edge.end_node.bsdd_data != end_node.bsdd_data:
                continue
            if edge.edge_type == edge_type:
                return edge
        return None

    @classmethod
    def get_edge_from_relation(
        cls, relation: BsddClassRelation | BsddPropertyRelation, bsdd_dictionary: BsddDictionary
    ):
        scene = cls.get_scene()
        if not scene:
            return None
        start_data, end_data, relation_type = cls.read_relation(relation, bsdd_dictionary)
        start_node, end_node = cls.get_node_from_bsdd_data(start_data), cls.get_node_from_bsdd_data(
            end_data
        )
        return cls.get_edge_from_nodes(start_node, end_node, relation_type)

    @classmethod
    def get_relation_from_edge(cls, edge: graphics_items.Edge, bsdd_dictionary: BsddDictionary):
        start_data, end_data = edge.start_node.bsdd_data, edge.end_node.bsdd_data
        if isinstance(start_data, BsddClass):
            if not isinstance(end_data, BsddClass):
                return
            end_uri = cl_utils.build_bsdd_uri(end_data, bsdd_dictionary)
            for rel in start_data.ClassRelations:
                if rel.RelatedClassUri == end_uri:
                    return rel
        elif isinstance(start_data, BsddProperty):
            if not isinstance(end_data, BsddProperty):
                return
            end_uri = prop_utils.build_bsdd_uri(end_data, bsdd_dictionary)
            for rel in start_data.PropertyRelations:
                if rel.RelatedPropertyUri == end_uri:
                    return rel

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
