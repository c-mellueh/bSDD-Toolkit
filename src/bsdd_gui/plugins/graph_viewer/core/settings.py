from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.settings import ui


def connect_signals(settings: Type[gv_tool.Settings], window: Type[gv_tool.Window]):
    settings.connect_internal_signals()
    window.signals.widget_created.connect(lambda w: create_widget(w, settings, window))


def create_widget(parent_window, settings: Type[gv_tool.Settings], window: Type[gv_tool.Window]):
    widget = settings.create_widget(parent_window)
    button_widget = widget.layout().add


def register_widget(widget: ui.SettingsWidget, settings: Type[gv_tool.Settings]):
    settings.register_widget(widget)


def connect_widget(widget: ui.SettingsWidget, setting: Type[gv_tool.Settings]):
    setting.connect_widget_signals(widget)
