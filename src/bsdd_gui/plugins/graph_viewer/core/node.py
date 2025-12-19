from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.node import ui


def connect_signals(
    node: Type[gv_tool.Node], edge: Type[gv_tool.Edge], project: Type[tool.Project]
):
    node.signals.remove_edge_requested.connect(
        lambda e, s, ov, ap: edge.remove_edge(
            e,
            s,
            project.get(),
            ov,
            ap,
        )
    )
