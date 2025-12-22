from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import bsdd_gui.plugins.graph_viewer.tool as gv_tool
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils

from bsdd_json import BsddClass, BsddDictionary, BsddProperty
from PySide6.QtCore import QCoreApplication, Qt, Signal, QPoint, QObject, QPointF, QRectF
from PySide6.QtGui import QDropEvent
from PySide6.QtWidgets import QLabel, QGraphicsItem

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.scene_view import ui, trigger, constants
from bsdd_gui.presets.tool_presets import PluginTool, PluginSignals
from bsdd_gui.module.class_tree_view.constants import JSON_MIME as CLASS_JSON_MIME
from bsdd_gui.module.property_table_widget.constants import JSON_MIME as PROPERTY_JSON_MIME

import qtawesome as qta

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.prop import GraphViewerSceneViewProperties
    from bsdd_gui.plugins.graph_viewer.module.edge import constants as edge_constants
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node


class Signals(PluginSignals):
    delete_selection_requested = Signal()
    classes_insert_requested = Signal(list, QPointF)
    properties_insert_requested = Signal(list, QPointF)
    recalculate_edges_requested = Signal()
    buchheim_requested = Signal()
    clear_scene_requested = Signal()
    center_scene_requested = Signal()
    export_requested = Signal()
    import_requested = Signal()
    load_bsdd_requested = Signal()
    toggle_running_requested = Signal()


class SceneView(PluginTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerSceneViewProperties:
        return bsdd_gui.GraphViewerSceneViewProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.delete_selection_requested.connect(trigger.delete_selection)
        cls.signals.classes_insert_requested.connect(trigger.insert_classes)
        cls.signals.properties_insert_requested.connect(trigger.insert_properties)
        cls.signals.recalculate_edges_requested.connect(trigger.recalculate_edges)
        cls.signals.load_bsdd_requested.connect(trigger.load_bsdd)
        cls.signals.center_scene_requested.connect(trigger.center_scene)
        cls.signals.export_requested.connect(trigger.export_requested)
        cls.signals.import_requested.connect(trigger.import_requested)

        return super().connect_internal_signals()

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def create_scene(cls):
        cls.get_properties().scene = ui.GraphScene()
        return cls.get_properties().scene

    @classmethod
    def connect_view(cls):
        view = cls.get_view()
        scene = view.scene()
        scene.changed.connect(lambda *_,: cls.update_help_overlay_visibility())

    @classmethod
    def set_edge_drag_active(cls, state: bool):
        """
        Edge-drawing interaction state
        """
        cls.get_properties()

    @classmethod
    def create_help_overlay(cls):
        view = cls.get_view()
        text = QCoreApplication.translate(
            "GraphViewer",
            "Drag & drop classes or properties in the view to edit their relations.\n"
            "Hold Shift and drag between nodes to create relations.\n"
            "Double-click an edge legend in the settings tab to change relation style.\n"
            "Editing Parent-Class-Code relations isn't supported so far.",
        )
        overlay = QLabel(text, view.viewport())
        overlay.setWordWrap(True)
        overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        overlay.setStyleSheet(constants.OVERLAY_STYLESHEET)
        cls.get_properties()._help_overlay = overlay
        cls.reposition_help_overlay()
        cls.update_help_overlay_visibility()

    @classmethod
    def reposition_help_overlay(cls):
        view = cls.get_view()
        overlay = cls.get_properties()._help_overlay
        overlay.adjustSize()

        if not overlay:
            return
        vp = view.viewport()
        if vp is None:
            return
        margin = 16
        max_w = int(min(720, vp.width() - 2 * margin))
        if max_w < 120:
            max_w = max(120, vp.width() - 2 * margin)
        try:
            overlay.setMaximumWidth(max_w)
            overlay.adjustSize()
        except Exception:
            pass
        w = min(overlay.width(), max_w)
        h = overlay.height()
        x = int((vp.width() - w) / 2)
        y = int((vp.height() - h) / 2)
        overlay.setGeometry(x, y, w, h)
        try:
            overlay.raise_()
        except Exception:
            pass

    @classmethod
    def update_help_overlay_visibility(cls):
        if not cls.get_properties()._help_overlay:
            return
        try:
            has_nodes = bool(cls.get_nodes())
        except Exception:
            has_nodes = True
        cls.get_properties()._help_overlay.setVisible(not has_nodes)

    @classmethod
    def get_selected_items(cls):
        from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge
        from bsdd_gui.plugins.graph_viewer.module.node.ui import Node

        scene = cls.get_scene()
        selected_nodes: list[Node] = []
        selected_edges: list[Edge] = []
        if not scene:
            return [], []
        try:
            selected = list(scene.selectedItems())
        except Exception:
            selected = []
        if not selected:
            return [], []
        for it in selected:
            if isinstance(it, Node):
                selected_nodes.append(it)
            elif isinstance(it, Edge):
                selected_edges.append(it)
        return selected_nodes, selected_edges

    @classmethod
    def request_delete_selection(cls):
        cls.signals.delete_selection_requested.emit()

    @classmethod
    def get_view(cls) -> ui.GraphView:
        return cls.get_properties().view

    @classmethod
    def set_view(cls, view: ui.GraphView):
        cls.get_properties().view = view

    @classmethod
    def get_scene(cls) -> ui.GraphScene:
        if not cls.get_properties().view:
            return None
        return cls.get_properties().view.scene()

    @classmethod
    def get_panning_mmb(cls) -> bool:
        return cls.get_properties()._panning_mmb

    @classmethod
    def set_panning_mmb(cls, value: bool):
        cls.get_properties()._panning_mmb = value

    @classmethod
    def get_pan_last_pos(cls):
        return cls.get_properties()._pan_last_pos

    @classmethod
    def set_pan_last_pos(cls, value: QPoint):
        cls.get_properties()._pan_last_pos = value

    @classmethod
    def create_scene_rect(cls):
        # Fit to visible nodes if any, with generous padding and minimum size
        scene = cls.get_scene()
        half = constants.SCENE_MIN_SIZE / 2.0
        scene.setSceneRect(QRectF(-half, -half, constants.SCENE_MIN_SIZE, constants.SCENE_MIN_SIZE))

    # --- Helper -------------------------------------------------------------
    @classmethod
    def _event_qpoint(cls, event) -> QPoint:
        try:
            p = event.position()
            return QPoint(int(p.x()), int(p.y()))
        except Exception:
            return event.pos()

    @classmethod
    def _item_at_pos(cls, pos_view: QPoint) -> QGraphicsItem | None:
        try:
            return cls.get_view().itemAt(pos_view)
        except Exception:
            # Fallback if itemAt signature differs
            return None

    @classmethod
    def add_item(cls, item: QGraphicsItem):
        cls.get_scene().addItem(item)

    @classmethod
    def remove_item(cls, item: QGraphicsItem):
        cls.get_scene().removeItem(item)

    @classmethod
    def get_nodes(cls) -> list[Node]:
        return gv_tool.Node.get_nodes()

    @classmethod
    def get_edges(cls) -> list[Edge]:
        return gv_tool.Edge.get_edges()

    @classmethod
    def apply_filters(cls, edge_filters: dict[str, bool], node_filters: dict[str, bool]):
        for n in cls.get_nodes():
            show = node_filters.get(n.node_type, True)
            n.setVisible(show)
        for e in cls.get_edges():
            show_edge = edge_filters.get(e.edge_type, True)
            show_edge = show_edge and e.start_node.isVisible() and e.end_node.isVisible()
            e.setVisible(show_edge)

    @classmethod
    def get_position_from_event(cls, event: QDropEvent):
        view = cls.get_view()
        try:
            pos_view = event.position()
            # mapToScene expects int coordinates
            scene_pos = view.mapToScene(int(pos_view.x()), int(pos_view.y()))
        except Exception:
            scene_pos = view.mapToScene(event.pos())
        return scene_pos

    # ---------- Drag & Drop --------------------------------------
    @classmethod
    def _mime_has_bsdd_class(cls, md) -> bool:

        try:
            if md.hasFormat(CLASS_JSON_MIME):
                return True
            if md.hasFormat("application/json"):
                return True
            if md.hasFormat("text/plain"):
                # expecting JSON array of codes as text
                return True
        except Exception:
            pass
        return False

    @classmethod
    def get_mime_type(cls, mime_data) -> constants.ALLOWED_DRAG_TYPES | None:
        if mime_data.hasFormat(PROPERTY_JSON_MIME):
            return constants.PROPERTY_DRAG
        if mime_data.hasFormat(CLASS_JSON_MIME):
            return constants.CLASS_DRAG
        return None

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
    def request_classes_insert(cls, classes: list[BsddClass], postion: QPointF):
        cls.signals.classes_insert_requested.emit(classes, postion)

    @classmethod
    def request_center_scene(cls):
        cls.signals.center_scene_requested.emit()

    @classmethod
    def request_properties_insert(cls, properties: list[BsddProperty], postion: QPointF):
        cls.signals.properties_insert_requested.emit(properties, postion)

    @classmethod
    def request_recalculate_edges(cls):
        cls.signals.recalculate_edges_requested.emit()

    @classmethod
    def request_clear_scene(cls):
        cls.signals.clear_scene_requested.emit()

    @classmethod
    def create_button_widget(cls):
        button_widget = ui.ButtonWidget()
        button_widget.bt_clear.setIcon(qta.icon("mdi6.cancel"))
        button_widget.bt_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
        button_widget.bt_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
        button_widget.bt_load.setIcon(qta.icon("mdi6.tray-full"))
        button_widget.bt_center.setIcon(qta.icon("mdi6.arrow-collapse-all"))
        button_widget.bt_start_stop.setIcon(qta.icon("mdi6.pause"))
        button_widget.bt_tree.setIcon(qta.icon("mdi6.graph"))
        cls.get_properties().button_widget = button_widget

        return cls.get_properties().button_widget

    @classmethod
    def connect_button_settings(cls):
        button_widget = cls.get_buttons_widget()
        button_widget.bt_load.clicked.connect(lambda _: trigger.load_bsdd())
        button_widget.bt_start_stop.clicked.connect(
            lambda _: cls.signals.toggle_running_requested.emit()
        )
        button_widget.bt_clear.clicked.connect(lambda _: cls.request_clear_scene())
        button_widget.bt_center.clicked.connect(lambda _: cls.request_center_scene())

        # Import/Export current graph layout (nodes + positions)
        button_widget.bt_export.clicked.connect(lambda _: cls.signals.export_requested.emit())
        button_widget.bt_import.clicked.connect(lambda _: cls.signals.import_requested.emit())
        button_widget.bt_tree.clicked.connect(lambda _: cls.signals.buchheim_requested.emit())

    @classmethod
    def get_buttons_widget(cls):
        return cls.get_properties().button_widget


# --- Import/Export ----------------------------------------------------
