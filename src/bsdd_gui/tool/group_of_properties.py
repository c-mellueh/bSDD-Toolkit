
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetTool,ActionTool,ItemViewTool
from bsdd_gui.module.group_of_properties.ui import GopWidget
from bsdd_gui.module.group_of_properties import trigger
if TYPE_CHECKING:
    from bsdd_gui.module.group_of_properties.prop import GroupOfPropertiesProperties


class GroupOfProperties(WidgetTool,ActionTool):
    @classmethod
    def get_properties(cls) -> GroupOfPropertiesProperties:
        return bsdd_gui.GroupOfPropertiesProperties

    @classmethod
    def connect_internal_signals(cls):
        return super().connect_internal_signals()
    
    @classmethod
    def connect_widget_signals(cls, widget):
        return super().connect_widget_signals(widget)
    
    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return GopWidget

class GopClassView(ItemViewTool):
    @classmethod
    def get_properties(cls) -> GopClassViewProperties:
        return bsdd_gui.GopClassViewProperties  