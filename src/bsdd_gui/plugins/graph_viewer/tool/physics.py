from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from PySide6.QtCore import QObject, QTimer
import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.physics import data, trigger
from bsdd_gui.presets.tool_presets import BaseTool

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.physics.prop import GraphViewerPhysicsProperties


class Signals(QObject):
    pass


class Physics(BaseTool):
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
    def get_running(cls) -> bool:
        return cls.get_properties().running
