from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from PySide6.QtCore import QModelIndex, QObject, Signal, Qt
from bsdd_parser.models import BsddClassProperty, BsddClass, BsddProperty
from bsdd_gui.module.property_table import ui, models, trigger


if TYPE_CHECKING:
    from bsdd_gui.module.property_table.prop import PropertyTableProperties

from bsdd_gui.presets.tool_presets import (
    ItemModelHandler,
    ViewHandler,
    ViewSignaller,
    WidgetSignaller,
    WidgetHandler,
    ModuleHandler,
)


class Signaller(ViewSignaller, WidgetSignaller):
    property_info_requested = Signal(BsddClassProperty)
    reset_all_property_tables_requested = Signal()
    new_property_requested = Signal()


class PropertyTable(ItemModelHandler, ViewHandler, ModuleHandler, WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyTableProperties:
        return bsdd_gui.PropertyTableProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signaller.widget_requested.connect(lambda _, p: trigger.create_widget(p))
        cls.signaller.widget_created.connect(trigger.widget_created)

    @classmethod
    def connect_widget_to_internal_signals(cls, widget: ui.PropertyWidget):
        pass

    @classmethod
    def request_new_property(cls):
        cls.signaller.new_property_requested.emit()

    @classmethod
    def create_widget(cls):
        widget = ui.PropertyWidget()
        cls.get_properties().widgets.add(widget)
        cls.signaller.widget_created.emit(widget)
        return widget

    @classmethod
    def create_model(cls):
        model = models.PropertyTableModel()
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model
