from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary
import bsdd_gui
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor
from bsdd_gui.plugins.graph_viewer.module.edge import ui, trigger, constants
from bsdd_gui.plugins.graph_viewer.module.node import constants as node_constants
from bsdd_gui.presets.tool_presets import BaseTool

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.prop import GraphViewerEdgeProperties


class Signals:
    active_edgetype_requested = Signal(str)


class Edge(BaseTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerEdgeProperties:
        return bsdd_gui.GraphViewerEdgeProperties

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.active_edgetype_requested.connect(trigger.set_active_edge)

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
    def request_active_edge(cls, value):
        cls.signals.active_edgetype_requested.emit(value)

    @classmethod
    def set_active_edge(cls, edge_type: constants.ALLOWED_EDGE_TYPES_TYPING | None):
        cls.get_properties().active_edge = edge_type

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
