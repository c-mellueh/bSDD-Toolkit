from __future__ import annotations

from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.scene_view import ui
    from bsdd_gui.plugins.graph_viewer.module.window import ui as ui_window

def connect_signals(window:Type[gv_tool.Window],scene_view:Type[gv_tool.SceneView]):
    window.signals.widget_created.connect(lambda w:w.view.setScene(scene_view.create_scene()))

