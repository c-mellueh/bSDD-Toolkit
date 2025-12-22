from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.settings import ui, trigger
from bsdd_gui.presets.tool_presets import WidgetTool, WidgetSignals

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.settings.prop import GraphViewerSettingsProperties

import qtawesome as qta


class Signals(WidgetSignals):
    expanded_changed = Signal(bool)


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
    def get_widget(cls) -> ui.SettingsWidget:
        widgets = cls.get_widgets()
        if len(widgets) == 0:
            return None
        return widgets[0]

    @classmethod
    def connect_widget_signals(cls, widget: ui.SettingsWidget):
        super().connect_widget_signals(widget)
        widget.expand_button.clicked.connect(cls.toggle_sidebar)



    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.SettingsWidget:
        return super().create_widget(*args, **kwargs)

    @classmethod
    def toggle_sidebar(cls):
        cls.set_expanded(not cls.is_expanded())

    @classmethod
    def set_expanded_width(cls, value: int):
        cls.get_properties().expanded_width = value

    @classmethod
    def get_expanded_width(cls) -> int:
        return cls.get_properties().expanded_width

    @classmethod
    def set_expanded(cls, value: bool):
        if cls.is_expanded() == value:
            return

        cls.get_properties().is_expanded = value
        widget = cls.get_widget()
        widget.expand_button.setCheckable(value)
        cls.apply_expanded_state()
        cls.signals.expanded_changed.emit(value)

    @classmethod
    def is_expanded(cls) -> bool:
        return cls.get_properties().is_expanded

    @classmethod
    def apply_expanded_state(cls) -> None:
        widget = cls.get_widget()
        widget.scroll_area.setVisible(cls.is_expanded())
        widget.expand_button.setIcon(
            qta.icon("mdi6.chevron-left") if not cls.is_expanded() else qta.icon("mdi6.chevron-right")
        )
        widget.updateGeometry()

    @classmethod
    def add_content_widget(cls, input_widget: QWidget, index=None) -> None:
        """Append an arbitrary widget below the edge-type panel inside the
        scroll area. Useful for adding legends or extra controls.
        """
        # Insert before the final stretch, so it stays at the bottom
        # but above the stretchable spacer
        widget = cls.get_widget()
        if index is None:
            index = widget.scroll_layout.count() - 1
            if index < 0:
                index = 0
        widget.scroll_layout.insertWidget(0,input_widget)
    @classmethod
    def position_and_resize(
        cls, viewport_width: int, viewport_height: int, margin: int = 0
    ) -> None:
        widget = cls.get_widget()
        if not widget:
            return
        """Anchor to top-right of the given viewport size and stretch to full height."""
        width = widget.expand_button.width() + (
            cls.get_expanded_width() if cls.is_expanded() else 0
        )
        x = max(0, viewport_width - width)
        y = margin
        h = max(0, viewport_height - 2 * margin)
        widget.setGeometry(x, y, width, h)
        widget.raise_()
