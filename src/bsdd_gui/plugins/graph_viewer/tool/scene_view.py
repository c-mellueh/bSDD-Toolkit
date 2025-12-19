from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import QCoreApplication, Qt, Signal
from PySide6.QtWidgets import QLabel

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.scene_view import ui, trigger, constants
from bsdd_gui.presets.tool_presets import BaseTool
from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.prop import GraphViewerSceneViewProperties


class Signals:
    delete_selection_requested = Signal(ui.GraphView)


class SceneView(BaseTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerSceneViewProperties:
        return bsdd_gui.GraphViewerSceneViewProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.delete_selection_requested.connect(trigger.delete_selection)
        return super().connect_internal_signals()

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def create_scene(cls):
        return ui.GraphScene()

    @classmethod
    def connect_view(cls, view: ui.GraphView):
        scene = view.scene()
        scene.changed.connect(lambda *_, v=view: cls.update_help_overlay_visibility(v))

    @classmethod
    def set_edge_drag_active(cls, state: bool):
        """
        Edge-drawing interaction state
        """
        cls.get_properties()

    @classmethod
    def create_help_overlay(cls, view: ui.GraphView):
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
        cls.reposition_help_overlay(view)
        cls.update_help_overlay_visibility(view)

    @classmethod
    def reposition_help_overlay(cls, view: ui.GraphView):
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
    def update_help_overlay_visibility(cls, view: ui.GraphView):
        if cls.get_properties()._help_overlay:
            return
        try:
            sc: ui.GraphScene = view.scene()
            has_nodes = bool(getattr(sc, "nodes", []) or [])
        except Exception:
            has_nodes = True
        cls.get_properties()._help_overlay.setVisible(not has_nodes)

    @classmethod
    def get_selected_items(cls, scene: ui.GraphScene):
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
    def toggle_running(cls, view: ui.GraphView):
        scene = view.scene()
        scene.running = not scene.running

    @classmethod
    def request_delete_selection(cls, view: ui.GraphScene):
        cls.signals.delete_selection_requested.emit(view)
