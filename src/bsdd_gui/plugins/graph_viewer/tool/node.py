from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal, QPointF, QObject
from PySide6.QtWidgets import QGraphicsItem, QWidget
import random
import bsdd_gui
from bsdd_json import BsddDictionary, BsddClass, BsddProperty
from bsdd_gui.presets.tool_presets import BaseDialog
from bsdd_gui.plugins.graph_viewer.module.node import ui, trigger, constants
from bsdd_gui.plugins.graph_viewer.module.edge import constants as edge_constants
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils

from bsdd_gui.module.ifc_helper.data import IfcHelperData

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.prop import GraphViewerNodeProperties
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge


class Signals(QObject):
    remove_edge_requested = Signal(
        object, object, bool, bool
    )  # edge,Scene, only visual, allow parent deletion
    node_created = Signal(ui.Node)


class Node(BaseDialog):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerNodeProperties:
        return bsdd_gui.GraphViewerNodeProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def remove_node(
        cls,
        node: ui.Node,
        scene: GraphScene,
        ignored_edges: list[Edge] = None,
    ):
        pass

        ignored_edges = list() if ignored_edges is None else ignored_edges
        if not scene:
            return
        for e in list(scene.edges):
            if e.edge_type != edge_constants.PARENT_CLASS and e in ignored_edges:
                continue
            if e.start_node == node or e.end_node == node:
                cls.signals.remove_edge_requested.emit(
                    e,
                    scene,
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
    def add_node(
        cls, bsdd_data: BsddClass | BsddProperty, pos=None, color=None, is_external=False
    ) -> ui.Node:
        n = ui.Node(bsdd_data, color=color, is_external=is_external)
        p = (
            pos
            if pos is not None
            else QPointF(random.uniform(-150, 150), random.uniform(-150, 150))
        )
        n.setPos(p)
        cls.signals.node_created.emit(n)
        return n

    @classmethod
    def add_ifc_node(
        cls, ifc_code: str, position: QPointF, ifc_classes: dict = None, external_nodes=None
    ) -> ui.Node | None:
        if not ifc_classes:
            ifc_classes = {c.get("code"): c for c in IfcHelperData.get_classes()}
        if not external_nodes:
            existing_nodes = {
                n
                for n in cls.get_nodes()
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
        new_node = cls.add_node(ifc_class, pos=position, is_external=True)
        return new_node

    # --- Helper -------------------------------------------------------------

    @classmethod
    def _node_from_item(cls, item: QGraphicsItem) -> Node | None:
        it = item
        while it is not None:
            if isinstance(it, Node):
                return it
            try:
                it = it.parentItem()
            except Exception:
                break
        return None

    @classmethod
    def get_filter_state(cls, key: constants.ALLOWED_NODE_TYPES_TYPING) -> bool:
        return cls.get_properties().filters.get(key, True)

    @classmethod
    def get_filters(cls):
        return cls.get_properties().filters

    @classmethod
    def set_filters(cls, key: str, value: bool):
        cls.get_properties().filters[key] = value

    @classmethod
    def get_nodes(cls):
        return cls.get_properties().nodes

    @classmethod
    def get_internal_nodes(cls, bsdd_dictionary: BsddDictionary):
        return {
            cl_utils.build_bsdd_uri(n.bsdd_data, bsdd_dictionary): n
            for n in cls.get_nodes()
            if n.node_type == constants.CLASS_NODE_TYPE
        }

    @classmethod
    def get_external_nodes(cls):
        return {n.bsdd_data.OwnedUri: n for n in cls.get_nodes() if n.is_external}

    @classmethod
    def get_uri_dict(cls, bsdd_dictionary: BsddDictionary):
        uri_dict = dict()

        for node in cls.get_nodes():
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
        return uri_dict
