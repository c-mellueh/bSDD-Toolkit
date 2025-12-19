from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6.QtCore import Signal, QCoreApplication
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.window import ui, trigger
from bsdd_gui.presets.tool_presets import ActionTool, FieldTool
from bsdd_gui.presets.signal_presets import FieldSignals

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.window.prop import GraphViewerWindowProperties
    from bsdd_gui.plugins.graph_viewer.module.edge import constants as edge_constants


class Signals(FieldSignals):
    toggle_running_requested = Signal()
    delete_selection_requested = Signal()
    active_edgetype_requested = Signal(object)


class Window(ActionTool, FieldTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerWindowProperties:
        return bsdd_gui.GraphViewerWindowProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        # Lazy import to avoid heavy cost on module load
        return ui.GraphWidget

    @classmethod
    def request_toggle_running(cls):
        cls.signals.toggle_running_requested.emit()

    @classmethod
    def request_delete_selection(cls):
        cls.signals.delete_selection_requested.emit()

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.toggle_running_requested.connect(lambda: print("TEST"))

    @classmethod
    def set_status(cls, text):
        widget: ui.GraphWidget = cls.get_widgets()[0]
        if text:
            widget.statusbar.showMessage(text)
        else:
            widget.statusbar.clearMessage()

    @classmethod
    def set_active_edge(cls, edge_type: edge_constants.ALLOWED_EDGE_TYPES_TYPING | None):
        cls.signals.active_edgetype_requested.emit(edge_type)
        text = QCoreApplication.translate("GraphViewer", "Create {} Relationship").format(edge_type)
        cls.set_status(text)
