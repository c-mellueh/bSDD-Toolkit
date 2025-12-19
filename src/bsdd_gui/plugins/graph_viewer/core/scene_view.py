from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.scene_view import ui
    from bsdd_gui.plugins.graph_viewer.module.window import ui as ui_window


def connect_signals(window: Type[gv_tool.Window], scene_view: Type[gv_tool.SceneView]):
    window.signals.widget_created.connect(lambda w: handle_widget_creation(w, scene_view))
    window.signals.toggle_running_requested.connect(scene_view.toggle_running)
    window.signals.delete_selection_requested.connect(scene_view.request_delete_selection)


def handle_widget_creation(widget: ui_window.GraphWidget, scene_view: Type[gv_tool.SceneView]):
    scene_view.set_view(widget.view)
    widget.view.setScene(scene_view.create_scene())
    scene_view.create_help_overlay()
    scene_view.connect_view()


def delete_selection(
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
):
    scene = scene_view.get_scene()
    bsdd_dictionary = project.get()
    selected_nodes, selected_edges = scene_view.get_selected_items()
    edges_to_remove = list(set(selected_edges))
    for e in edges_to_remove:
        edge.remove_edge(edge, scene, bsdd_dictionary)

    for n in selected_nodes:
        node.remove_node(n, scene, ignored_edges=edges_to_remove)
