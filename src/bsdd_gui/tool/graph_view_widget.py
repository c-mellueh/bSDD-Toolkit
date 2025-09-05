from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import ActionTool, WidgetTool

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.prop import GraphViewWidgetProperties


from bsdd_gui.module.graph_view_widget import trigger


class GraphViewWidget(ActionTool, WidgetTool):
    @classmethod
    def get_properties(cls) -> GraphViewWidgetProperties:
        return bsdd_gui.GraphViewWidgetProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        # Lazy import to avoid heavy cost on module load
        from bsdd_gui.module.graph_view_widget.ui import GraphWindow

        return GraphWindow

    @classmethod
    def create_widget(cls, parent=None):
        # Instantiate the top-level GraphWindow. Parent is optional.
        widget = cls._get_widget_class()(parent)
        # cls.register_widget(widget)
        return widget
