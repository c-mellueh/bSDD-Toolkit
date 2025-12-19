from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_json import BsddDictionary
from bsdd_gui.plugins.graph_viewer.module.node import ui, trigger

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.node.prop import GraphViewerNodeProperties
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge


class Signals:
    pass


class Node:
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
        bsdd_dictionary: BsddDictionary,
        ignored_edges: list[Edge] = None,
    ):
        pass
        # TODO
        # ignored_edges = list() if ignored_edges is None else ignored_edges

        # scene = cls.get_scene()
        # if not scene:
        #     return
        # for e in list(scene.edges):
        #     if e.edge_type != constants.PARENT_CLASS and e in ignored_edges:
        #         continue
        #     if e.start_node == node or e.end_node == node:
        #         cls.remove_edge(
        #             e,
        #             bsdd_dictionary=bsdd_dictionary,
        #             only_visual=True,
        #             allow_parent_deletion=True,
        #         )

        # try:
        #     scene.removeItem(node)
        # except Exception:
        #     pass
        # try:
        #     scene.nodes.remove(node)
        # except ValueError:
        #     pass
