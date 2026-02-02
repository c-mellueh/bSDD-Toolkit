
from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import FieldTool,ActionTool,ItemViewTool,FieldSignals,ViewSignals
from bsdd_gui.module.group_of_properties.ui import GopWidget
from bsdd_gui.module.group_of_properties import trigger,models,views
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from .class_tree_view import ClassTreeView as CTV
from .class_tree_view import Signals as CTS

if TYPE_CHECKING:
    from bsdd_gui.module.group_of_properties.prop import GroupOfPropertiesProperties,GopClassViewProperties


class WidgetSignals(FieldSignals):
    widget_requested = Signal(object,QWidget) #bSDDDictionary, Window


class GroupOfProperties(FieldTool,ActionTool):
    signals = WidgetSignals()

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


class ClassViewSignals(CTS):
    pass

class GopClassView(CTV):
    signals = ClassViewSignals()
    @classmethod
    def get_properties(cls) -> GopClassViewProperties:
        return bsdd_gui.GopClassViewProperties  
    
    @classmethod
    def _get_model_class(cls):
        return  models.ClassTreeModel
    
    @classmethod
    def _get_trigger(cls):
        return trigger
    
    @classmethod
    def _get_proxy_model_class(cls):
        return models.SortModel
    
    @classmethod
    def delete_selection(view):
        return super().delete_selection()