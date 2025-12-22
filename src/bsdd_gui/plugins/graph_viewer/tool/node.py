from __future__ import annotations
from typing import TYPE_CHECKING, Optional
import logging
from PySide6.QtCore import Signal, QPointF, QObject, QCoreApplication, Qt, QRectF
from PySide6.QtWidgets import QGraphicsItem, QHBoxLayout, QLabel, QApplication
from PySide6.QtGui import QColor, QPen, QBrush, QFontMetrics, QPainterPath, QPainter
import random
import bsdd_gui
from bsdd_json import BsddDictionary, BsddClass, BsddProperty
from bsdd_gui.presets.tool_presets import PluginTool, PluginSignals
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


class Signals(PluginSignals):
    remove_edge_requested = Signal(
        object, object, bool, bool
    )  # edge,Scene, only visual, allow parent deletion
    node_created = Signal(ui.Node)
    node_double_clicked = Signal(ui.Node)
    node_changed = Signal(QGraphicsItem.GraphicsItemChange, ui.Node)
    filter_changed = Signal(str, bool)


class Node(PluginTool):
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
    def calculate_node_type(cls, node: ui.Node):
        bsdd_data, is_external = node.bsdd_data, node.is_external
        if isinstance(bsdd_data, BsddProperty):
            if is_external:
                node_type = constants.EXTERNAL_PROPERTY_NODE_TYPE
            else:
                node_type = constants.PROPERTY_NODE_TYPE
        elif isinstance(bsdd_data, BsddClass):
            if cl_utils.is_ifc_reference(bsdd_data):
                node_type = constants.IFC_NODE_TYPE
            elif is_external:
                node_type = constants.EXTERNAL_CLASS_NODE_TYPE
            else:
                node_type = constants.CLASS_NODE_TYPE
        else:
            node_type = "generic"
        return node_type

    @classmethod
    def setup_node(cls, node: ui.Node):

        node.node_type = cls.calculate_node_type(node)
        node.color = cls.get_color(node.node_type)
        node.brush = QBrush(node.color)
        node.border = QPen(QColor(40, 60, 90), 1.2)
        node.border.setCosmetic(True)
        node.node_shape = cls.get_shape(node.node_type)
        flags = (
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
            | QGraphicsItem.ItemIsSelectable
        )
        node.setFlags(flags)
        node.setAcceptHoverEvents(True)
        node.double_clicked.connect(lambda n=node: cls.signals.node_double_clicked.emit(n))
        node.item_changed.connect(lambda c, n=node: cls.signals.node_changed.emit(c, n))

    @classmethod
    def add_node(cls, bsdd_data: BsddClass | BsddProperty, pos=None, is_external=False) -> ui.Node:
        n = ui.Node(bsdd_data, is_external=is_external)
        cls.setup_node(n)

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
    def _node_from_item(cls, item: QGraphicsItem) -> ui.Node | None:
        it = item
        while it is not None:
            if isinstance(it, ui.Node):
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
    def get_class_nodes(cls) -> list[ui.Node]:
        return [n for n in cls.get_nodes() if n.node_type == constants.CLASS_NODE_TYPE]

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
        title = QLabel(QCoreApplication.translate("GraphViewer", "Node Types"))
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
            sw.toggled.connect(lambda _, nt=node_type: cls.toggle_filter_state(nt))
            row.addWidget(icon, 0)
            row.addWidget(lbl, 1)
            row.addWidget(sw, 0, alignment=Qt.AlignRight)
            rows.append(row)
        return rows

    @classmethod
    def path_from_node_shape(
        cls, node_shape: constants.ALLOWED_NODE_SHAPES_TYPING, width: float, height: float
    ) -> QPainterPath:
        path = QPainterPath()
        if node_shape == constants.SHAPE_STYPE_ELLIPSE:
            path.addEllipse(QRectF(-width / 2, -height / 2, width, height))
        elif node_shape == constants.SHAPE_STYLE_ROUNDED_RECT:
            path.addRoundedRect(QRectF(-width / 2, -height / 2, width, height), 6, 6)
        elif node_shape == constants.SHAPE_STYLE_RECT:  # rect
            path.addRect(QRectF(-width / 2, -height / 2, width, height))
        return path

    @classmethod
    def _update_size_for_text(cls, node: ui.Node, painter: Optional[QPainter] = None):
        # Compute size from current font metrics so the rectangle fits the text
        try:
            fm = painter.fontMetrics() if painter is not None else QFontMetrics(QApplication.font())
        except Exception:
            return  # can't compute metrics safely right now
        tr = fm.boundingRect(node.label)
        pad_x, pad_y = cls.get_properties().text_padding
        new_w = tr.width() + 2 * pad_x
        new_h = tr.height() + 2 * pad_y
        # Avoid excessive geometry changes for tiny fluctuations
        if abs(new_w - node._w) > 0.5 or abs(new_h - node._h) > 0.5:
            node.prepareGeometryChange()
            node._w = new_w
            node._h = new_h

    @classmethod
    def _collect_layout(cls) -> dict:
        nodes = cls.get_nodes()
        nodes_payload = []
        for n in nodes:
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
    def import_node_from_json(
        cls, item: dict, bsdd_dictionary: BsddDictionary, ifc_classes, external_nodes
    ):
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
            node = cls.add_node(bsdd_obj, pos=QPointF(x, y))
            return node
        except Exception:
            return

    @classmethod
    def get_node_from_bsdd_data(cls, bsdd_data: BsddClass | BsddProperty) -> ui.Node | None:
        for node in cls.get_nodes():
            if node.bsdd_data == bsdd_data:
                return node
        return None

    @classmethod
    def get_node_from_ifc_code(cls, ifc_code: str):

        for node in cls.get_nodes():
            if node.is_external and node.bsdd_data.Code == ifc_code:
                return node
