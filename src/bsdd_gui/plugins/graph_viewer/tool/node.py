from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal, QPointF, QObject, QCoreApplication, Qt
from PySide6.QtWidgets import QGraphicsItem, QHBoxLayout, QLabel
from PySide6.QtGui import QColor
import random
import bsdd_gui
from bsdd_json import BsddDictionary, BsddClass, BsddProperty
from bsdd_gui.presets.tool_presets import BaseTool
from bsdd_gui.plugins.graph_viewer.module.node import ui, trigger, constants
from bsdd_gui.plugins.graph_viewer.module.edge import constants as edge_constants
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils

import bsdd_gui.plugins.graph_viewer.tool as gv_tool
from bsdd_gui.module.ifc_helper.data import IfcHelperData
from bsdd_gui.presets.ui_presets import ToggleSwitch

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.prop import GraphViewerNodeProperties
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge


class Signals(QObject):
    remove_edge_requested = Signal(
        object, object, bool, bool
    )  # edge,Scene, only visual, allow parent deletion
    node_created = Signal(ui.Node)
    remove_node_requested = Signal(ui.Node)
    node_double_clicked = Signal(ui.Node)
    filter_changed = Signal(str, bool)


class Node(BaseTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerNodeProperties:
        return bsdd_gui.GraphViewerNodeProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.node_double_clicked.connect(trigger.node_double_clicked)
        super().connect_internal_signals()

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def clear(cls):
        cls.get_properties().nodes = list()

    @classmethod
    def remove_node(
        cls,
        node: ui.Node,
        scene: GraphScene,
        ignored_edges: list[Edge] = None,
    ):
        if node not in cls.get_nodes():
            return
        ignored_edges = list() if ignored_edges is None else ignored_edges
        for e in list(gv_tool.Edge.get_edges()):
            if e.edge_type != edge_constants.PARENT_CLASS and e in ignored_edges:
                continue
            if e.start_node == node or e.end_node == node:
                cls.signals.remove_edge_requested.emit(e, scene, True, True)

        scene.removeItem(node)
        cls.get_properties().nodes.remove(node)

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
    def get_color(cls, node_type: constants.ALLOWED_NODE_TYPES_TYPING):
        return cls.get_properties().color_map.get(node_type, constants.NODE_COLOR_DEFAULT)

    @classmethod
    def get_shape(cls, node_type: constants.ALLOWED_NODE_TYPES_TYPING):
        return cls.get_properties().shape_map.get(node_type, constants.SHAPE_STYLE_RECT)

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
        cls.signals.filter_changed.emit(key, value)

    @classmethod
    def toggle_filter_state(cls, node_type: str):
        cls.set_filters(node_type, not cls.get_filter_state(node_type))

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

    @classmethod
    def emit_node_double_clicked(cls, node: ui.Node):
        cls.signals.node_double_clicked.emit(node)

    @classmethod
    def get_node_name(cls, node_type: constants.ALLOWED_NODE_TYPES_TYPING):
        l = constants.NODE_TYPE_LABEL_MAP.get(str(node_type), str(node_type))
        return QCoreApplication.translate("GraphViewer", l)

    @classmethod
    def get_allowed_node_types(cls):
        return cls.get_properties().allowed_nodes_types

    @classmethod
    def create_settings_widget(cls):
        widget = ui.NodeTypeSettingsWidget()
        cls.get_properties().settings_widget = widget
        title = QLabel(QCoreApplication.translate("GraphViewSettings", "Node Types"))
        title.setObjectName("titleLabel")
        widget.layout().addWidget(title)
        return widget

    @classmethod
    def create_node_toggles(cls):
        rows = list()
        for node_type in cls.get_allowed_node_types():
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            icon = ui._NodeLegendIcon(str(node_type))
            name = cls.get_node_name(node_type)
            lbl = QLabel(name)
            lbl.setToolTip(name)
            sw = ToggleSwitch(checked=True)
            sw.toggled.connect(lambda _,nt=node_type: cls.toggle_filter_state(nt))
            row.addWidget(icon, 0)
            row.addWidget(lbl, 1)
            row.addWidget(sw, 0, alignment=Qt.AlignRight)
            rows.append(row)
        return rows

    @classmethod
    def create_pen(cls, node_type: constants.ALLOWED_NODE_TYPES_TYPING):
        cls.get_col
