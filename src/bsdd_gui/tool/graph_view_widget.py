
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.prop import GraphViewWidgetProperties


class GraphViewWidget:
    @classmethod
    def get_properties(cls) -> GraphViewWidgetProperties:
        return bsdd_gui.GraphViewWidgetProperties
