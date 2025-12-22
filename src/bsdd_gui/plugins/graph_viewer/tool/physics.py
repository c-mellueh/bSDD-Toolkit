from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import QObject, QTimer, Signal
import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.physics import data, trigger, ui
from bsdd_gui.presets.tool_presets import PluginTool, PluginSignals

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.physics.prop import GraphViewerPhysicsProperties


class Signals(PluginSignals):
    is_running_changed = Signal(bool)


class Physics(PluginTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerPhysicsProperties:
        return bsdd_gui.GraphViewerPhysicsProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def connect_internal_signals(cls):
        return super().connect_internal_signals()

    @classmethod
    def create_physics(cls):
        cls.get_properties().physics = data.Physics()
        return cls.get_properties().physics

    @classmethod
    def get_physics(cls):
        return cls.get_properties().physics

    @classmethod
    def create_timer(cls):
        timer = QTimer()
        timer.setInterval(30)
        timer.timeout.connect(trigger.tick)
        cls.get_properties().timer = timer
        return cls.get_properties().timer

    @classmethod
    def get_timer(cls):
        return cls.get_properties().timer

    @classmethod
    def set_running(cls, value: bool):
        cls.get_properties().running = value

    @classmethod
    def is_running(cls) -> bool:
        return cls.get_properties().running

    @classmethod
    def toggle_running(cls):
        cls.set_running(not cls.is_running())
        cls.signals.is_running_changed.emit(cls.is_running())
        return

    @classmethod
    def get_auto_paused(cls) -> bool:
        return cls.get_properties().auto_paused

    @classmethod
    def set_auto_paused(cls, value: bool):
        cls.get_properties().auto_paused = value

    @classmethod
    def handle_hide(cls, _=None):
        if not cls.is_running():
            return
        cls.set_running(False)
        cls.set_auto_paused(True)

    @classmethod
    def handle_shown(cls, _=None):
        if cls.get_auto_paused():
            cls.set_running(True)
            cls.set_auto_paused(False)

    @classmethod
    def create_settings_widget(cls):
        widget = ui.SettingsWidget()
        cls.get_properties().settings_widget = widget

        # Avoid feedback loops by blocking signals while setting initial values
        widget.sl_l0.blockSignals(True)
        widget.sl_ks.blockSignals(True)
        widget.sl_rep.blockSignals(True)
        physics = cls.get_properties().physics
        try:
            widget.sl_l0.setValue(int(physics.spring_length))
            widget.sl_ks.setValue(int(physics.k_spring * 100))
            widget.sl_rep.setValue(int(physics.k_repulsion))
        finally:
            widget.sl_l0.blockSignals(False)
            widget.sl_ks.blockSignals(False)
            widget.sl_rep.blockSignals(False)
        return cls.get_properties().settings_widget

    @classmethod
    def connect_settings_widget(cls):
        physics = cls.get_properties().physics

        def handle_value_change(_):
            physics.spring_length = float(widget.sl_l0.value())
            physics.k_spring = float(widget.sl_ks.value()) / 1000.0
            physics.k_repulsion = float(widget.sl_rep.value())

        widget = cls.get_properties().settings_widget
        widget.sl_l0.valueChanged.connect(handle_value_change)
        widget.sl_ks.valueChanged.connect(handle_value_change)
        widget.sl_rep.valueChanged.connect(handle_value_change)
