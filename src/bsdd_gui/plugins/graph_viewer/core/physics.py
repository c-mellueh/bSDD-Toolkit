from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.physics import ui


def connect_signals(
    phyiscs: Type[gv_tool.Physics],
    window: Type[gv_tool.Window],
    settings: Type[gv_tool.Settings],
    scene_view: Type[gv_tool.SceneView],
):
    phyiscs.connect_internal_signals()
    window.signals.widget_created.connect(lambda _: build_phyiscs(phyiscs))
    window.signals.widget_hidden.connect(phyiscs.handle_hide)
    window.signals.widget_shown.connect(phyiscs.handle_shown)
    settings.signals.widget_created.connect(lambda sw: add_settings(phyiscs, settings))
    window.signals.toggle_running_requested.connect(phyiscs.toggle_running)
    scene_view.signals.toggle_running_requested.connect(phyiscs.toggle_running)


def disconnect_signals(physics: Type[gv_tool.Physics]):
    physics.disconnect_internal_signals()
    physics.disconnect_external_signals()


def build_phyiscs(phyiscs: Type[gv_tool.Physics]):
    ph = phyiscs.create_physics()
    timer = phyiscs.create_timer()
    phyiscs.set_running(True)
    timer.start()


def add_settings(phyiscs: Type[gv_tool.Physics], settings: Type[gv_tool.Settings]):
    widget = phyiscs.create_settings_widget()
    phyiscs.connect_settings_widget()
    settings.add_content_widget(widget)


def tick(
    phyiscs: Type[gv_tool.Physics],
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
    scene_view: Type[gv_tool.SceneView],
):
    if not phyiscs.is_running() or not node.get_nodes():
        return
    ph = phyiscs.get_physics()
    scene = scene_view.get_scene()
    ph.gravity_center = scene.sceneRect().center()
    # Only simulate visible items
    vis_nodes = [n for n in node.get_nodes() if n.isVisible()]
    vis_edges = [
        e
        for e in edge.get_edges()
        if e.isVisible() and e.start_node.isVisible() and e.end_node.isVisible()
    ]
    if vis_nodes:
        ph.step(vis_nodes, vis_edges, dt=1.0)
    # Update visible edges' geometry
    for e in vis_edges:
        edge.requeste_path_update(e)
