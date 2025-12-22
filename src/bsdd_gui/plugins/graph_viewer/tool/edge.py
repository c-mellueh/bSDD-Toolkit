from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary
import bsdd_gui
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import class_utils as cl_utils

from bsdd_json import (
    BsddClass,
    BsddProperty,
    BsddClassProperty,
    BsddDictionary,
    BsddClassRelation,
    BsddPropertyRelation,
)
from PySide6.QtCore import Signal, Qt, QPointF, QObject, QCoreApplication
from PySide6.QtGui import QColor, QPen, QPainterPath, QPolygonF, QBrush
from PySide6.QtWidgets import QGraphicsPathItem, QHBoxLayout, QLabel, QGraphicsItem
from bsdd_gui.plugins.graph_viewer.module.edge import ui, trigger, constants
from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants
from bsdd_gui.presets.tool_presets import BaseTool
from bsdd_gui.presets.ui_presets import ToggleSwitch

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.prop import GraphViewerEdgeProperties
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
from bsdd_gui.module.ifc_helper.data import IfcHelperData

RelationsDict = dict[constants.ALLOWED_EDGE_TYPES_TYPING, dict[tuple[str, str, str, str], ui.Edge]]


class Signals(QObject):
    activate_edgetype_requested = Signal(str)
    edge_drag_started = Signal(QGraphicsPathItem)
    edge_drag_finished = Signal(QGraphicsPathItem)
    new_class_property_created = Signal(object)
    new_edge_created = Signal(ui.Edge)
    ifc_reference_removed = Signal(object, str)
    ifc_reference_added = Signal(BsddClass, str)
    edge_removed = Signal(ui.Edge)
    class_relation_removed = Signal(BsddClassRelation)
    class_property_removed = Signal(BsddClassProperty, BsddClass)
    property_relation_removed = Signal(BsddPropertyRelation)
    edge_hide_requested = Signal(str)
    filter_changed = Signal(str, bool)


class Edge(BaseTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerEdgeProperties:
        return bsdd_gui.GraphViewerEdgeProperties

    @classmethod
    def get_edge_class(cls) -> Type[ui.Edge]:
        return ui.Edge

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.activate_edgetype_requested.connect(trigger.set_active_edge)
        cls.signals.new_edge_created.connect(lambda e: cls.get_properties().edges.append(e))

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def clear(cls):
        cls.get_properties().edges = list()

    @classmethod
    def remove_edge(
        cls,
        edge: ui.Edge,
        scene: GraphScene,
        bsdd_dictionary: BsddDictionary,
        only_visual=False,
        allow_parent_deletion=False,
    ):
        if not edge in cls.get_edges():
            return

        start_node, end_node = edge.start_node, edge.end_node
        relation_type = edge.edge_type
        if relation_type == constants.GENERIC_REL:
            return

        if relation_type == constants.PARENT_CLASS and not allow_parent_deletion:
            return

        scene.removeItem(edge)
        cls.get_properties().edges.remove(edge)

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
                if end_node.is_external:
                    class_property = {
                        cp.PropertyUri: cp for cp in start_data.ClassProperties if cp.PropertyUri
                    }.get(end_data.OwnedUri)
                else:
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
    def create_edge(cls, start_node: Node, end_node: Node, edge_type) -> ui.Edge:
        edge = ui.Edge(start_node, end_node, edge_type)
        cls.requeste_path_update(edge)
        cls.update_pen(edge)
        if edge.edge_type != constants.PARENT_CLASS:
            edge.setFlag(QGraphicsItem.ItemIsSelectable, True)
        return edge

    @classmethod
    def get_edges(cls) -> list[ui.Edge]:
        return cls.get_properties().edges

    @classmethod
    def add_edge(
        cls,
        edge: ui.Edge,
    ) -> ui.Edge | None:

        for existing_edge in cls.get_edges():
            if existing_edge.start_node.bsdd_data != edge.start_node.bsdd_data:
                continue
            if existing_edge.end_node.bsdd_data != edge.end_node.bsdd_data:
                continue
            if existing_edge.edge_type == edge.edge_type:
                logging.info(f"Edge allread exists {edge}")
                return

        cls.signals.new_edge_created.emit(edge)
        return edge

    @classmethod
    def request_active_edge(cls, value):
        cls.signals.activate_edgetype_requested.emit(value)

    @classmethod
    def set_active_edge(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING | None):
        cls.get_properties().active_edge = edge_type

    @classmethod
    def get_filter_state(cls, key: constants.ALLOWED_EDGE_TYPES_TYPING) -> bool:
        return cls.get_properties().filters.get(key, True)

    @classmethod
    def get_filters(cls):
        return cls.get_properties().filters

    @classmethod
    def set_filters(cls, key: constants.ALLOWED_EDGE_TYPES_TYPING, value: bool):
        cls.get_properties().filters[key] = value
        cls.signals.filter_changed.emit(key, value)

    @classmethod
    def toggle_filter_state(cls, edge_type: str):
        cls.set_filters(edge_type, not cls.get_filter_state(edge_type))

    @classmethod
    def get_active_edge(cls) -> constants.ALLOWED_EDGE_TYPES_TYPING | None:
        return cls.get_properties().active_edge

    @classmethod
    def is_edge_drag_active(cls):
        return cls.get_properties().edge_drag_active

    @classmethod
    def set_edge_drag_active(cls, value: bool):
        cls.get_properties().edge_drag_active = value

    @classmethod
    def get_edge_stylesheet(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
        color = cls.get_edge_color(edge_type)
        width = cls.get_edge_width(edge_type)
        style = cls.get_edge_style(edge_type)

        css_style = "solid"
        try:
            if style == Qt.PenStyle.DotLine:
                css_style = "dotted"
            elif style in (
                Qt.PenStyle.DashLine,
                Qt.PenStyle.DashDotLine,
                Qt.PenStyle.DashDotDotLine,
            ):
                css_style = "dashed"
        except Exception:
            css_style = "solid"
        if isinstance(color, QColor):
            r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        else:
            r, g, b, a = 130, 130, 150, 255
        css = f"QGraphicsView {{ border: {max(1, int(round(width)))}px {css_style} rgba({r}, {g}, {b}, 255); }}"
        return css

    @classmethod
    def _start_edge_drag(cls, start_node: Node, scene_pos: QPointF) -> None:
        cls.set_edge_drag_active(True)

        cls.get_properties().edge_drag_start_node = start_node
        # Create a lightweight preview path
        path_item = QGraphicsPathItem()
        pen = QPen(QColor(200, 200, 210, 220))
        pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        pen.setWidthF(1.2)
        path_item.setPen(pen)
        path_item.setZValue(-0.5)  # above edges (-1), below nodes (0)
        cls.signals.edge_drag_started.emit(path_item)
        cls.get_properties().edge_preview_item = path_item
        cls._update_edge_drag(scene_pos)

    @classmethod
    def _update_edge_drag(cls, scene_pos: QPointF) -> None:
        is_active = cls.is_edge_drag_active()
        preview_item = cls.get_properties().edge_preview_item
        start_node = cls.get_properties().edge_drag_start_node

        if not is_active or preview_item is None or start_node is None:
            return

        start_pos = start_node.pos()
        p = QPainterPath()
        p.moveTo(start_pos)
        # Match the scene's routing mode for the preview path

        if not cls.is_orthogonal_mode():
            p.lineTo(scene_pos)
        else:
            # Create a short stub that leaves the node perpendicular (axis-aligned)
            dx = scene_pos.x() - start_pos.x()
            dy = scene_pos.y() - start_pos.y()
            stub_len = 14.0
            if abs(dx) >= abs(dy):
                s1 = QPointF(start_pos.x() + (stub_len if dx >= 0 else -stub_len), start_pos.y())
                m = QPointF(s1.x(), scene_pos.y())
            else:
                s1 = QPointF(start_pos.x(), start_pos.y() + (stub_len if dy >= 0 else -stub_len))
                m = QPointF(scene_pos.x(), s1.y())
            p.lineTo(s1)
            p.lineTo(m)
            p.lineTo(scene_pos)
        preview_item.setPath(p)

    @classmethod
    def _finish_edge_drag(cls, end_node: Node | None) -> None:
        # Remove preview
        if cls.get_properties().edge_preview_item is not None:
            cls.signals.edge_drag_finished.emit(cls.get_properties().edge_preview_item)
            cls.get_properties().edge_preview_item = None

        start_node = cls.get_properties().edge_drag_start_node
        # Reset state
        cls.get_properties().edge_drag_active = False
        cls.get_properties().edge_drag_start_node = None

        if start_node is None or end_node is None:
            return
        if end_node is start_node:
            return

        # Decide edge type: use selected type if set, otherwise heuristic
        trigger.create_relation(start_node, end_node, cls.get_active_edge())

    # -- Create Relations ------------------------------------------
    @classmethod
    def create_class_property_relation(
        cls,
        start_node: Node,
        end_node: Node,
        bsdd_dictionary: BsddDictionary,
    ):
        bsdd_class = (
            start_node.bsdd_data
            if start_node.node_type == node_constants.CLASS_NODE_TYPE
            else end_node.bsdd_data
        )
        bsdd_property = (
            start_node.bsdd_data
            if start_node.node_type
            in [node_constants.PROPERTY_NODE_TYPE, node_constants.EXTERNAL_PROPERTY_NODE_TYPE]
            else end_node.bsdd_data
        )

        # check if relationship exists allready
        for bsdd_class_property in bsdd_class.ClassProperties:
            if bsdd_property == prop_utils.get_property_by_class_property(
                bsdd_class_property, bsdd_dictionary
            ):
                return

        new_property = prop_utils.create_class_property_from_property(
            bsdd_property, bsdd_class, bsdd_dictionary
        )
        new_property._set_parent(bsdd_class)
        bsdd_class.ClassProperties.append(new_property)
        cls.signals.new_class_property_created.emit(new_property)
        new_edge = cls.create_edge(start_node, end_node, edge_type=constants.C_P_REL)
        cls.add_edge(new_edge)

    @classmethod
    def create_class_class_relation(
        cls,
        start_node: Node,
        end_node: Node,
        bsdd_dictionary: BsddDictionary,
        relation: constants.ALLOWED_EDGE_TYPES_TYPING,
    ):
        start_class: BsddClass = start_node.bsdd_data
        end_class: BsddClass = end_node.bsdd_data

        if relation not in constants.CLASS_RELATIONS:
            return
        if relation == constants.IFC_REFERENCE_REL:
            if not end_node.node_type == node_constants.IFC_NODE_TYPE:
                return
            rienl = [x.lower() for x in start_class.RelatedIfcEntityNamesList or []]
            if end_class.Code.lower() not in rienl:
                start_class.RelatedIfcEntityNamesList.append(end_class.Code)
                cls.signals.ifc_reference_added.emit(start_class, end_class.Code)

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
        cls.add_edge(new_edge)

    @classmethod
    def create_property_property_relation(
        cls,
        start_node: Node,
        end_node: Node,
        bsdd_dictionary: BsddDictionary,
        relation: constants.ALLOWED_EDGE_TYPES_TYPING,
    ):
        start_property: BsddProperty = start_node.bsdd_data
        end_property: BsddProperty = end_node.bsdd_data

        if relation not in constants.PROPERTY_RELATIONS:
            return

        if end_node.is_external:
            end_uri = end_property.OwnedUri
        else:
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
        cls.add_edge(new_edge)

    @classmethod
    def get_relations_dict(cls, bsdd_dictionary: BsddDictionary):
        relations_dict: RelationsDict = {et: dict() for et in constants.ALLOWED_EDGE_TYPES}
        for edge in cls.get_edges():
            info = cls._info(edge.start_node, edge.end_node, bsdd_dictionary)
            if info in relations_dict[edge.edge_type]:
                logging.info(f"Relationship duplicate found")
            relations_dict[edge.edge_type][info] = edge
        return relations_dict

    @classmethod
    def find_class_relations(
        cls,
        nodes: list[Node],
        uri_dict: dict[str, Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], ui.Edge]],
        bsdd_dictionary: BsddDictionary,
    ) -> list[ui.Edge]:
        new_edges = list()
        for start_node in nodes:
            if start_node.node_type != node_constants.CLASS_NODE_TYPE:
                continue
            start_class = start_node.bsdd_data
            parent_class = cl_utils.get_class_by_code(bsdd_dictionary, start_class.ParentClassCode)
            if parent_class:
                parent_uri = cl_utils.build_bsdd_uri(parent_class, bsdd_dictionary)
                related_node = uri_dict.get(parent_uri)
                relation_type = constants.PARENT_CLASS
                info = cls._info(start_node, related_node, bsdd_dictionary)

                if related_node is not None and info not in existing_relations_dict[relation_type]:
                    edge = cls.create_edge(
                        start_node, related_node, edge_type=constants.PARENT_CLASS
                    )
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
    def find_class_property_relations(
        cls,
        nodes: list[Node],
        uri_dict: dict[str, Node],
        existing_relations_dict: RelationsDict,
        bsdd_dictionary: BsddDictionary,
    ) -> list[ui.Edge]:

        new_edges = list()
        for start_node in nodes:
            if start_node.node_type != node_constants.CLASS_NODE_TYPE:
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
        nodes: list[Node],
        uri_dict: dict[str, Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], ui.Edge]],
        bsdd_dictionary: BsddDictionary,
    ) -> list[ui.Edge]:
        new_edges = list()
        for start_node in nodes:
            if start_node.node_type != node_constants.PROPERTY_NODE_TYPE:
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
    def find_ifc_relations(
        cls,
        nodes: list[Node],
        uri_dict: dict[str, Node],
        existing_relations_dict: dict[str, dict[tuple[str, str, str, str], ui.Edge]],
        bsdd_dictionary: BsddDictionary,
    ):
        ifc_dict = {c["code"]: c for c in IfcHelperData.get_classes()}
        new_edges = list()
        relation_type = constants.IFC_REFERENCE_REL
        for start_node in nodes:
            if start_node.node_type != node_constants.CLASS_NODE_TYPE or start_node.is_external:
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
    def _info(
        cls,
        start_node: Node,
        end_node: Node,
        bsdd_dictionary: BsddDictionary,
    ):
        def get_uri_from_node(node: Node, bsdd_dictionary: BsddDictionary):
            if node.node_type in [
                node_constants.EXTERNAL_CLASS_NODE_TYPE,
                node_constants.EXTERNAL_PROPERTY_NODE_TYPE,
                node_constants.IFC_NODE_TYPE,
            ]:
                uri = node.bsdd_data.OwnedUri
            elif node.node_type == node_constants.CLASS_NODE_TYPE:
                uri = cl_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
            elif node.node_type == node_constants.PROPERTY_NODE_TYPE:
                uri = prop_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
            else:
                uri = None
            return uri

        d = [None, None, None, None]
        d[0] = start_node.node_type
        d[1] = get_uri_from_node(start_node, bsdd_dictionary)
        if end_node:
            d[2] = end_node.node_type
            d[3] = get_uri_from_node(end_node, bsdd_dictionary)
        return tuple(d)

    @classmethod
    def get_allowed_edge_types(cls) -> list[constants.ALLOWED_EDGE_TYPES_TYPING]:
        return cls.get_properties().allowed_edge_types

    @classmethod
    def get_edgetype_name(cls, key: str):
        text = constants.EDGE_TYPE_LABEL_MAP.get(str(key), str(key))
        QCoreApplication.translate("GaphViewer", text)
        return text

    @classmethod
    def request_edge_hide(cls, edge_type: str):
        cls.signals.edge_hide_requested(edge_type)

    @classmethod
    def create_pen_for_edgestyle(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
        color = cls.get_edge_color(edge_type)
        width = cls.get_edge_width(edge_type)
        style = cls.get_edge_style(edge_type)
        pen = QPen(color if isinstance(color, QColor) else QColor(130, 130, 150))
        pen.setCosmetic(True)
        pen.setWidthF(width)
        pen.setStyle(style)
        return pen

    # ------- Settings ------------------------

    @classmethod
    def get_edge_style_map(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING) -> dict:
        return constants.EDGE_STYLE_MAP.get(edge_type, constants.EDGE_STYLE_DEFAULT)

    @classmethod
    def get_edge_color(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
        style = cls.get_edge_style_map(edge_type)
        return style.get("color", constants.EDGE_STYLE_DEFAULT["color"])

    @classmethod
    def get_edge_style(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
        style = cls.get_edge_style_map(edge_type)
        return style.get("style", constants.EDGE_STYLE_DEFAULT["style"])

    @classmethod
    def get_edge_width(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
        style = cls.get_edge_style_map(edge_type)
        return float(style.get("width", constants.EDGE_STYLE_DEFAULT["width"]))

    @classmethod
    def is_orthogonal_mode(cls) -> bool:
        return cls.get_properties().orthogonal_edges

    @classmethod
    def set_orthogonal_mode(cls, value: bool):
        cls.get_properties().orthogonal_edges = value
        for e in cls.get_edges():
            cls.requeste_path_update(e)

    @classmethod
    def is_edge_type_enabled(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING):
        return cls.get_edge_style_map(edge_type).get("enabled")

    @classmethod
    def create_edge_type_settings_widget(cls) -> ui.EdgeTypeSettingsWidget:
        widget = ui.EdgeTypeSettingsWidget()
        cls.get_properties().edge_type_settings_widget = widget
        title = QLabel(QCoreApplication.translate("GraphViewer", "Edge Types"))
        title.setObjectName("titleLabel")
        widget.layout().addWidget(title)
        return widget

    @classmethod
    def create_edge_toggles(cls):
        toggles = list()
        for edge_type in cls.get_allowed_edge_types():
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(6)
            icon = ui._EdgeLegendIcon(str(edge_type))
            icon.edgeTypeActivated.connect(cls.signals.activate_edgetype_requested.emit)
            name = cls.get_edgetype_name(edge_type)
            label = QLabel(name)
            label.setToolTip(name)
            switch = ToggleSwitch(checked=True)
            switch.toggled.connect(lambda _, et=edge_type: cls.toggle_filter_state(et))
            switch.setChecked(cls.is_edge_type_enabled(edge_type))
            row.addWidget(icon, 0)
            row.addWidget(label, 1)
            row.addWidget(switch, 0, alignment=Qt.AlignmentFlag.AlignRight)
            toggles.append(row)
        return toggles

    @classmethod
    def create_edge_routing_settings_widget(cls) -> ui.EdgeRoutingWidget:
        widget = ui.EdgeRoutingWidget()
        cls.get_properties().edge_routing_settings_widget = widget
        widget.checkBox.toggled.connect(
            lambda: cls.set_orthogonal_mode(not cls.is_orthogonal_mode())
        )
        return widget

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
            end_data = prop_utils.get_property_by_uri(related_uri, bsdd_dictionary)
        return start_data, end_data, relation_type

    @classmethod
    def get_connected_edges(cls, node: Node) -> set[ui.Edge]:
        connected_edges = set()
        for edge in cls.get_edges():
            if edge.start_node == node or edge.end_node == node:
                connected_edges.add(edge)
        return connected_edges

    @classmethod
    def get_edge_from_nodes(
        cls,
        start_node: Node,
        end_node: Node | str,
        edge_type: str,
    ) -> ui.Edge | None:
        for edge in cls.get_edges():
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
        from bsdd_gui.plugins.graph_viewer.tool import Node as NodeTool

        start_data, end_data, relation_type = cls.read_relation(relation, bsdd_dictionary)
        start_node, end_node = NodeTool.get_node_from_bsdd_data(
            start_data
        ), NodeTool.get_node_from_bsdd_data(end_data)
        return cls.get_edge_from_nodes(start_node, end_node, relation_type)

    @classmethod
    def get_relation_from_edge(cls, edge: ui.Edge, bsdd_dictionary: BsddDictionary):
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

        # ---------- Edge Drawing ----------------------

    @classmethod
    def requeste_path_update(cls, edge: ui.Edge):
        trigger.update_path(edge)

    @classmethod
    def update_pen(cls, edge: ui.Edge):
        # Style edges using registry; falls back to default
        edge_type = edge.edge_type
        color = cls.get_edge_color(edge_type)
        width = cls.get_edge_width(edge_type)
        style = cls.get_edge_style(edge_type)
        pen = QPen(color if isinstance(color, QColor) else QColor(130, 130, 150), width)
        pen.setCosmetic(True)
        try:
            pen.setStyle(style)  # type: ignore[arg-type]
        except Exception:
            pen.setStyle(Qt.SolidLine)
        edge.setPen(pen)
        # No fill for arrow head
        edge._arrow_brush = QBrush(Qt.NoBrush)

    @classmethod
    def _calculate_anchor_on_node(cls, node: Node, toward: QPointF):
        """Return point on node boundary in direction of 'toward'.
        Approximates node shape as its rectangle for rect/roundedrect, and
        as ellipse for ellipse shape.
        """

        c = node.pos()
        v = QPointF(toward.x() - c.x(), toward.y() - c.y())
        length = (v.x() ** 2 + v.y() ** 2) ** 0.5
        if length < 1e-6:
            return QPointF(c)
        normalized_x, normalized_y = v.x() / length, v.y() / length

        half_width, half_height = getattr(node, "_w", 24.0) / 2.0, getattr(node, "_h", 24.0) / 2.0
        # Ellipse intersection distance from center along direction u
        if getattr(node, "node_shape", None) == node_constants.SHAPE_STYPE_ELLIPSE:
            import math

            denom = (normalized_x / max(half_width, 1e-6)) ** 2 + (
                normalized_y / max(half_height, 1e-6)
            ) ** 2
            t = 1.0 / math.sqrt(max(denom, 1e-9))
        else:
            # Rect/roundedrect: distance to edge along u
            tx = half_width / abs(normalized_x) if abs(normalized_x) > 1e-6 else float("inf")
            ty = half_height / abs(normalized_y) if abs(normalized_y) > 1e-6 else float("inf")
            t = min(tx, ty)
        if not cls.is_orthogonal_mode():
            return QPointF(c.x() + normalized_x * t, c.y() + normalized_y * t)

        if abs(v.y()) < half_height:
            dw = normalized_x / abs(normalized_x) * half_width
            return QPointF(c.x() + dw, c.y())
        else:
            dh = normalized_y / abs(normalized_y) * half_height
            return QPointF(c.x(), c.y() + dh)

    @classmethod
    def _ortho_mode_is_hor(cls, node: Node, toward: QPointF):
        c = node.pos()
        v = QPointF(toward.x() - c.x(), toward.y() - c.y())
        return abs(v.y()) < cls.get_properties().arrow_length * 3

    @classmethod
    def _ortho_start(cls, node: Node, toward: QPointF, hor_mode):
        c = node.pos()
        v = QPointF(toward.x() - c.x(), toward.y() - c.y())
        halfe_width, half_height = getattr(node, "_w", 24.0) / 2.0, getattr(node, "_h", 24.0) / 2.0
        if hor_mode:
            dw = v.x() / abs(v.x()) * halfe_width if abs(v.x()) > 1e-6 else 0.0
            return QPointF(c.x() + dw, c.y())
        else:
            dh = v.y() / abs(v.y()) * half_height if abs(v.y()) > 1e-6 else 0.0
            return QPointF(c.x(), c.y() + dh)

    @classmethod
    def _compute_arrow(cls, p1: QPointF, p2: QPointF) -> QPolygonF:
        """Create an arrowhead polygon at p2, pointing from p1 -> p2."""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        d = (dx * dx + dy * dy) ** 0.5
        if d < 1e-6:
            return QPolygonF()
        ux, uy = dx / d, dy / d
        # Orthogonal vector

        nx, ny = -uy, ux
        tail_x = p2.x() - ux * cls.get_properties().arrow_length
        tail_y = p2.y() - uy * cls.get_properties().arrow_length
        half_w = cls.get_properties().arrow_width / 2.0
        left = QPointF(tail_x + nx * half_w, tail_y + ny * half_w)
        right = QPointF(tail_x - nx * half_w, tail_y - ny * half_w)
        return QPolygonF([p2, left, right])

    @classmethod
    def draw_straight_line(cls, path: QPainterPath, p_start: QPointF, p_end_tip: QPointF):
        path.moveTo(p_start)
        # Straight line with arrow margin
        v = QPointF(p_end_tip.x() - p_start.x(), p_end_tip.y() - p_start.y())
        d = (v.x() ** 2 + v.y() ** 2) ** 0.5
        if d > 1e-6:
            ux, uy = v.x() / d, v.y() / d
            p_end_line = QPointF(
                p_end_tip.x() - ux * cls.get_properties().arrow_length,
                p_end_tip.y() - uy * cls.get_properties().arrow_length,
            )
            last_base = QPointF(p_start)
        else:
            p_end_line = QPointF(p_end_tip)
            last_base = QPointF(p_start)
        path.lineTo(p_end_line)
        return last_base

    @classmethod
    def draw_ortho_line(
        cls, path: QPainterPath, p_start: QPointF, p_end_tip: QPointF, horizontal_mode: bool
    ):
        delta_x = p_end_tip.x() - p_start.x()
        delta_y = p_end_tip.y() - p_start.y()
        x_dir = delta_x / abs(delta_x) if abs(delta_x) > 1e-6 else 0.0
        y_dir = delta_y / abs(delta_y) if abs(delta_y) > 1e-6 else 0.0
        if horizontal_mode:
            x_height = p_end_tip.x() - cls.get_properties().arrow_length * x_dir * 3
            p1 = QPointF(x_height, p_start.y())
            p2 = QPointF(x_height, p_end_tip.y())
            p3 = QPointF(p_end_tip.x() - x_dir * cls.get_properties().arrow_length, p_end_tip.y())

        else:
            y_height = p_end_tip.y() - cls.get_properties().arrow_length * y_dir * 3
            p1 = QPointF(p_start.x(), y_height)
            p2 = QPointF(p_end_tip.x(), y_height)
            p3 = QPointF(p_end_tip.x(), p_end_tip.y() - y_dir * cls.get_properties().arrow_length)
        path.moveTo(p_start)
        path.lineTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        return QPointF(p3)

    @classmethod
    def get_selected_pen(cls, edge: ui.Edge):
        """
        Return PenStyle for Selected edges
        """
        base_pen = edge.pen()
        glow_color = QColor(base_pen.color())
        try:
            glow_color.setAlpha(110)
        except Exception:
            pass
        glow_width = max(float(base_pen.widthF()) * 5.0, 10.0)
        glow_pen = QPen(glow_color, glow_width)
        glow_pen.setCosmetic(True)
        try:
            glow_pen.setStyle(Qt.SolidLine)
            glow_pen.setCapStyle(Qt.RoundCap)
            glow_pen.setJoinStyle(Qt.RoundJoin)
        except Exception:
            pass
        return glow_pen
