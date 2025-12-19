from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.scene_view import ui
    from bsdd_gui.plugins.graph_viewer.module.window import ui as ui_window


def connect_signals(window: Type[gv_tool.Window], scene_view: Type[gv_tool.SceneView]):
    window.signals.widget_created.connect(lambda w: handle_widget_creation(w, scene_view))
    window.signals.toggle_running_requested.connect(lambda w: scene_view.toggle_running(w.view))
    window.signals.delete_selection_requested.connect(
        lambda w: scene_view.request_delete_selection(w.view)
    )


def handle_widget_creation(widget: ui_window.GraphWidget, scene_view: Type[gv_tool.SceneView]):
    widget.view.setScene(scene_view.create_scene())
    scene_view.create_help_overlay(widget.view)
    scene_view.connect_view(widget.view)


def delete_selection(
    view: ui.GraphView,
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
):
    scene = view.scene()
    bsdd_dictionary = project.get()
    selected_nodes, selected_edges = scene_view.get_selected_items(scene)
    edges_to_remove = list(set(selected_edges))
    for e in edges_to_remove:
        edge.remove_edge(edge, scene, bsdd_dictionary)

    for n in selected_nodes:
        node.remove_node(n, scene, project.get(), ignored_edges=edges_to_remove)
