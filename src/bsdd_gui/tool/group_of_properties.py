from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from bsdd_json import BsddClass
import bsdd_gui
from bsdd_gui.presets.tool_presets import (
    FieldTool,
    ActionTool,
    ItemViewTool,
    FieldSignals,
    ViewSignals,
)
from bsdd_gui.module.group_of_properties import trigger, models, views, ui
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, QCoreApplication
from .class_tree_view import ClassTreeView as CTV
from .class_tree_view import Signals as CTS
from .class_property_table_view import ClassPropertyTableView as PTW
from .class_property_table_view import Signals as PTS

if TYPE_CHECKING:
    from bsdd_gui.module.group_of_properties.prop import (
        GroupOfPropertiesProperties,
        GopClassViewProperties,
        GopPropertyViewProperties,
    )


class WidgetSignals(FieldSignals):
    widget_requested = Signal(object, QWidget)  # bSDDDictionary, Window
    new_class_requested = Signal(str)


class GroupOfProperties(FieldTool, ActionTool):
    signals = WidgetSignals()

    @classmethod
    def get_properties(cls) -> GroupOfPropertiesProperties:
        return bsdd_gui.GroupOfPropertiesProperties

    @classmethod
    def connect_internal_signals(cls):
        return super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.GopWidget):
        super().connect_widget_signals(widget)

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls):
        return ui.GopWidget

    @classmethod
    def update_class_selection(
        cls, view: views.ClassView, widget: ui.GopWidget, bsdd_class: BsddClass
    ):
        if widget.tv_class != view:
            return
        text = QCoreApplication.translate("GroupOfProperties", "Group of properties: {}")
        widget.lb_class.setText(text.format(bsdd_class.Name if bsdd_class else ""))
        widget.glw_property.setEnabled(bsdd_class is not None)
        cls.get_properties().active_class = bsdd_class

    @classmethod
    def get_active_class(cls) -> BsddClass:
        return cls.get_properties().active_class


class ClassViewSignals(CTS):
    new_class_requested = Signal(str, views.ClassView)


class GopClassView(CTV):
    signals = ClassViewSignals()

    @classmethod
    def get_properties(cls) -> GopClassViewProperties:
        return bsdd_gui.GopClassViewProperties

    @classmethod
    def _get_model_class(cls):
        return models.ClassTreeModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.ClassSortModel

    @classmethod
    def get_allowed_class_types(cls):
        return ["GroupOfProperties"]

    @classmethod
    def request_new_class(cls, view: views.ClassView):
        text = "|".join(cls.get_allowed_class_types())
        cls.signals.new_class_requested.emit(text, view)


class PropertyViewSignals(PTS):
    pass


class GopPropertyView(PTW):
    signals = PropertyViewSignals()

    @classmethod
    def get_properties(cls) -> GopPropertyViewProperties:
        return bsdd_gui.GopPropertyViewProperties

    @classmethod
    def _get_model_class(cls):
        return models.PropertyTableModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.PropertySortModel
