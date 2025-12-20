from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.settings import ui


def connect_signals(
    settings: Type[gv_tool.Settings],
    window: Type[gv_tool.Window],
    scene_view: Type[gv_tool.SceneView],
):
    settings.connect_internal_signals()

    def reposition(*_, **__):
        viewport = scene_view.get_view().viewport()
        margin = 6
        settings.position_and_resize(viewport.width(), viewport.height(), margin)

    window.signals.widget_created.connect(lambda w: settings.create_widget())
    settings.signals.expanded_changed.connect(reposition)
    window.signals.widget_resized.connect(reposition)
    window.signals.widget_shown.connect(reposition)
    window.signals.widget_closed.connect(lambda: settings.unregister_widget(settings.get_widget()))


def create_widget(settings: Type[gv_tool.Settings]):
    settings.create_widget()


def register_widget(
    widget: ui.SettingsWidget, settings: Type[gv_tool.Settings], scene_view: Type[gv_tool.SceneView]
):
    settings.register_widget(widget)

    viewport = scene_view.get_view().viewport()

    settings.apply_expanded_state()
    widget.setParent(viewport)
    widget.show()
    settings.position_and_resize(viewport.width(), viewport.height(), 6)


def connect_widget(widget: ui.SettingsWidget, setting: Type[gv_tool.Settings]):
    setting.connect_widget_signals(widget)
