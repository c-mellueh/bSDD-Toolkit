from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.settings import ui, trigger
from bsdd_gui.presets.tool_presets import WidgetTool, WidgetSignals

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.settings.prop import GraphViewerSettingsProperties

import qtawesome as qta


class Signals(WidgetSignals):
    toggle_sidebar_requested = Signal()


class Settings(WidgetTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerSettingsProperties:
        return bsdd_gui.GraphViewerSettingsProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.SettingsWidget

    @classmethod
    def connect_internal_signals(cls):
        return super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.SettingsWidget):
        super().connect_widget_signals(widget)
        widget.expand_button.clicked.connect(cls.request_toggle_sidebar)

    @classmethod
    def create_button_widget(cls):
        button_widget = ui.ButtonWidget()
        button_widget.bt_clear.setIcon(qta.icon("mdi6.cancel"))
        button_widget.bt_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
        button_widget.bt_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
        button_widget.bt_load.setIcon(qta.icon("mdi6.tray-full"))
        button_widget.bt_center.setIcon(qta.icon("mdi6.arrow-collapse-all"))
        button_widget.bt_start_stop.setIcon(qta.icon("mdi6.pause"))
        button_widget.bt_tree.setIcon(qta.icon("mdi6.graph"))
        cls.get_properties().button_widget = button_widget

        return cls.get_properties().button_widget

    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.SettingsWidget:
        return super().create_widget(*args, **kwargs)

    @classmethod
    def request_toggle_sidebar(cls):
        cls.signals.toggle_sidebar_requested.emit()

    @classmethod
    def set_expanded_width(cls, value: int):
        cls.get_properties().expanded_width = value

    @classmethod
    def get_expanded_width(cls) -> int:
        return cls.get_properties().expanded_width

    @classmethod
    def set_expanded(cls, value: bool):
        cls.get_properties().is_expanded = value

    @classmethod
    def is_expanded(cls) -> bool:
        return cls.get_properties().is_expanded
