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
    property_info_requested = Signal(BsddProperty, ui.PropertyWidget)
    reset_all_property_tables_requested = Signal()
    new_property_requested = Signal()
    active_property_changed = Signal(object)


class PropertyTable(ItemModelHandler, ViewHandler, ModuleHandler, WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyTableProperties:
        return bsdd_gui.PropertyTableProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signaller.widget_requested.connect(lambda _, p: trigger.create_widget(p))
        cls.signaller.widget_created.connect(trigger.widget_created)
        cls.signaller.active_property_changed.connect(lambda _: cls.reset_views())

    @classmethod
    def connect_widget_to_internal_signals(cls, widget: ui.PropertyWidget):

        w = widget

        def handle_double_click(index: QModelIndex):
            proxy_model: models.SortModel = w.tv_properties.model()
            i = proxy_model.mapToSource(index)
            bsdd_property = i.siblingAtColumn(0).internalPointer()
            cls.signaller.property_info_requested.emit(bsdd_property, w)

        widget.tv_properties.doubleClicked.connect(handle_double_click)
        widget.tb_new.clicked.connect(
            lambda _, w=widget: cls.signaller.new_property_requested.emit()
        )

        def handle_prop_change(new_prop: BsddProperty):
            code = new_prop.Code if new_prop else ""
            w.lb_property_name.setText(code)

        cls.signaller.active_property_changed.connect(handle_prop_change)

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
    def create_property_model(cls):
        model = models.PropertyTableModel()
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def create_class_model(cls):
        model = models.ClassTableModel()
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def get_active_property(cls) -> BsddProperty:
        return cls.get_properties().active_property

    @classmethod
    def set_active_property(cls, value: BsddProperty):
        cls.get_properties().active_property = value
        cls.signaller.active_property_changed.emit(value)
