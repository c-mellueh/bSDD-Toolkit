from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGraphicsItem

import bsdd_gui
from bsdd_json import BsddDictionary
from bsdd_gui.presets.tool_presets import BaseDialog
from bsdd_gui.plugins.graph_viewer.module.node import ui, trigger, constants
from bsdd_gui.plugins.graph_viewer.module.edge import constants as edge_constants

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.prop import GraphViewerNodeProperties
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge


class Signals:
    remove_edge_requested = Signal(
        object, object, bool, bool
    )  # edge,Scene, only visual, allow parent deletion


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