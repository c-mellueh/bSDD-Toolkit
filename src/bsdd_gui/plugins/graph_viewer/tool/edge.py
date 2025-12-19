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
from PySide6.QtCore import Signal, Qt, QPointF
from PySide6.QtGui import QColor, QPen, QPainterPath
from PySide6.QtWidgets import QGraphicsPathItem
from bsdd_gui.plugins.graph_viewer.module.edge import ui, trigger, constants
from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants
from bsdd_gui.presets.tool_presets import BaseTool

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.prop import GraphViewerEdgeProperties
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node


class Signals:
    active_edgetype_requested = Signal(str)
    edge_drag_started = Signal(QGraphicsPathItem)
    edge_drag_finished = Signal(QGraphicsPathItem)
    new_class_property_created = Signal(object)
    new_edge_created = Signal(ui.Edge)
    ifc_reference_removed = Signal(object, str)
    edge_removed = Signal(ui.Edge)
    class_relation_removed = Signal(BsddClassRelation)
    class_property_removed = Signal(BsddClassProperty, BsddClass)
    property_relation_removed = Signal(BsddPropertyRelation)


class Edge(BaseTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerEdgeProperties:
        return bsdd_gui.GraphViewerEdgeProperties

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.active_edgetype_requested.connect(trigger.set_active_edge)
        cls.signals.new_edge_created.connect(lambda e: cls.get_properties().edges.append(e))

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def remove_edge(
        cls,
        edge: ui.Edge,
        scene: GraphScene,
        bsdd_dictionary: BsddDictionary,
        only_visual=False,
        allow_parent_deletion=False,
    ):
        pass

        if edge is None:
            return

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
    def create_edge(
        cls,
        start_node: Node,
        end_node: Node,
        edge_type,
        weight: float = 1.0,
    ):
        return Edge(start_node, end_node, edge_type, weight)

    @classmethod
    def get_edges(cls) -> list[ui.Edge]:
        return cls.get_properties().edges

    @classmethod
    def add_edge(
        cls,
        edge: ui.Edge,
    ) -> ui.Edge:

        for existing_edge in cls.get_edges():
            if existing_edge.start_node.bsdd_data != edge.start_node.bsdd_data:
                continue
            if existing_edge.end_node.bsdd_data != edge.end_node.bsdd_data:
                continue
            if existing_edge.edge_type == edge.edge_type:
                logging.info(f"Edge allread exists {edge}")
                return None
        cls.signals.new_edge_created.emit(edge)
        return edge

    @classmethod
    def request_active_edge(cls, value):
        cls.signals.active_edgetype_requested.emit(value)

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

    @classmethod
    def get_active_edge(cls) -> constants.ALLOWED_EDGE_TYPES_TYPING | None:
        return cls.get_properties().active_edge

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
    def set_orthogonal_mode(cls, value: str):
        cls.get_properties().orthogonal_edges = value

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
