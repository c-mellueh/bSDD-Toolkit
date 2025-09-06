from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPointF

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, WidgetTool

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.prop import GraphViewWidgetProperties
from bsdd_json import BsddDictionary, BsddClass, BsddProperty
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils

from bsdd_gui.module.graph_view_widget import trigger, ui, constants, view
from bsdd_gui.module.graph_view_widget.graphics_items import Node
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import JSON_MIME as PROPERTY_JSON_MIME


class GraphViewWidget(ActionTool, WidgetTool):
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
    def populate_from_bsdd(cls, widget: ui.GraphWindow, bsdd_dict: BsddDictionary):
        # Build graph from bSDD model: Classes and Properties
        widget.scene.clear_graph()

        # Node registries
        class_by_code: dict[str, Node] = {}
        class_by_uri: dict[str, Node] = {}
        prop_by_code: dict[str, Node] = {}
        prop_by_uri: dict[str, Node] = {}

        # 1) Classes
        for c in bsdd_dict.Classes:
            n = widget.scene.add_node(c)
            class_by_code[c.Code] = n
            try:
                uri = cl_utils.build_bsdd_uri(c, bsdd_dict)
                if uri:
                    class_by_uri[uri] = n
            except Exception:
                pass

        # 2) Properties (dictionary-level)
        for p in bsdd_dict.Properties:
            n = widget.scene.add_node(p)
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
                    widget.scene.add_edge(cnode, target_node, weight=1.0, edge_type="class_to_prop")

        # 4) ClassRelations edges (Class -> Class)
        for c in bsdd_dict.Classes:
            src_node = class_by_code.get(c.Code)
            if not src_node:
                continue
            dst_node = class_by_code.get(c.ParentClassCode)
            if not dst_node:
                continue
            widget.scene.add_edge(src_node, dst_node, weight=1.0, edge_type="class_rel")
            # for rel in c.ClassRelations:
            #     dst_node = class_by_uri.get(rel.RelatedClassUri)
            #     if dst_node is not None:
            #         self.scene.add_edge(
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
                    widget.scene.add_edge(src_node, dst, weight=0.0, edge_type="prop_rel")

        # No ClassProperty nodes are created; edges Class→Property were added above.

        # Apply current filters to the newly created graph
        widget._apply_filters()

    @classmethod
    def get_widget(cls):
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
    def get_position_from_event(cls, event: QDropEvent, gv: view):
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
    def insert_classes_in_scene(
        cls, scene: view.GraphScene, classes: list[BsddClass], position: QPointF
    ):
        offset_step = QPointF(24.0, 18.0)
        cur = QPointF(position)
        existing_class_codes = {
            n.bsdd_data.Code
            for n in scene.nodes
            if hasattr(n, "bsdd_data") and n.node_type == constants.CLASS_NODE_TYPE
        }

        for bsdd_class in classes:
            if bsdd_class.Code in existing_class_codes:
                continue
            n = scene.add_node(bsdd_class, pos=cur)
            cur += offset_step

    @classmethod
    def insert_properties_in_scene(
        cls, scene: view.GraphScene, bsdd_properties: list[BsddProperty], position: QPointF
    ):
        offset_step = QPointF(24.0, 18.0)
        cur = QPointF(position)
        existing_property_codes = {
            n.bsdd_data.Code
            for n in scene.nodes
            if hasattr(n, "bsdd_data") and n.node_type == constants.PROPERTY_NODE_TYPE
        }

        for bsdd_property in bsdd_properties:
            if bsdd_property.Code in existing_property_codes:
                continue
            n = scene.add_node(bsdd_property, pos=cur)
            cur += offset_step
