from __future__ import annotations
from typing import TYPE_CHECKING, Type
import logging

import bsdd_gui
from PySide6.QtCore import (
    QModelIndex,
    QObject,
    Signal,
    Qt,
    QSortFilterProxyModel,
    QItemSelectionModel,
)
from PySide6.QtWidgets import QWidget, QAbstractItemView, QTreeView
from bsdd_json.models import BsddClassProperty, BsddClass, BsddProperty, BsddDictionary
from bsdd_gui.module.property_table_widget import ui, models, trigger, views


if TYPE_CHECKING:
    from bsdd_gui.module.property_table_widget.prop import PropertyTableWidgetProperties

from bsdd_gui.presets.tool_presets import (
    ItemViewTool,
    ItemViewTool,
    ViewSignals,
    FieldSignals,
    WidgetTool,
    ActionTool,
)


class Signals(ViewSignals, FieldSignals):
    property_info_requested = Signal(BsddProperty, ui.PropertyWidget)
    reset_all_property_tables_requested = Signal()
    new_property_requested = Signal()
    active_property_changed = Signal(object)
    bsdd_class_double_clicked = Signal(object)
    search_requested = Signal(QWidget)


class PropertyTableWidget(ItemViewTool, ActionTool, WidgetTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> PropertyTableWidgetProperties:
        return bsdd_gui.PropertyTableWidgetProperties

    @classmethod
    def create_model(cls, data):
        logging.info(
            f"Create Model not isable in this module use create_class_model and create_property_model"
        )
        return None

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_widget_class(cls) -> Type[ui.PropertyWidget]:
        return ui.PropertyWidget

    @classmethod
    def add_property_to_dictionary(cls, bsdd_property, bsdd_dictionary: BsddDictionary):
        # TODO: Model handling
        affected_models = [
            m
            for m in cls.get_models()
            if m.bsdd_dictionary == bsdd_dictionary and isinstance(m, models.PropertyTableModel)
        ]
        for model in affected_models:
            row = model.rowCount()
            model.beginInsertRows(QModelIndex(), row, row)

        bsdd_dictionary.Properties.append(bsdd_property)
        for model in affected_models:
            model.endInsertRows()
        cls.signals.item_added.emit(bsdd_property)

    @classmethod
    def delete_selection(cls, view: views.ClassTable | views.PropertyTable):

        selected_elements = cls.get_selected(view)
        if not selected_elements:
            return
        bsdd_dictionary = view.model().sourceModel().bsdd_dictionary
        affected_models = [m for m in cls.get_models() if m.bsdd_dictionary == bsdd_dictionary]

        if isinstance(selected_elements[0], BsddProperty):
            affected_models = [
                m for m in affected_models if isinstance(m, models.PropertyTableModel)
            ]
            for bsdd_property in selected_elements:
                for model in affected_models:
                    row = model.get_row_for_data(bsdd_property)
                    model.beginRemoveRows(QModelIndex(), row, row)
                bsdd_dictionary.Properties.remove(bsdd_property)
                cls.signals.item_removed.emit(bsdd_property)
                for model in affected_models:
                    model.endRemoveRows()

        elif isinstance(selected_elements[0], BsddClass):
            affected_models = [m for m in affected_models if isinstance(m, models.ClassTableModel)]
            selected_elements: list[BsddClass]
            active_prop = cls.get_active_property()
            for bsdd_class in selected_elements:
                for model in affected_models:
                    row = model.get_row_for_data(bsdd_class)
                    model.beginRemoveRows(QModelIndex(), row, row)
                    model._data = None
                for bsdd_class_property in list(bsdd_class.ClassProperties):
                    if bsdd_class_property.PropertyCode == active_prop.Code:
                        bsdd_class.ClassProperties.remove(bsdd_class_property)
                        cls.signals.item_removed.emit(bsdd_class_property)
                for model in affected_models:
                    model.endRemoveRows()

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.selection_changed.connect(cls.on_selection_change)
        cls.signals.search_requested.connect(trigger.search_requested)

    @classmethod
    def connect_widget_signals(cls, widget: ui.PropertyWidget):
        super().connect_widget_signals(widget)
        w = widget

        def handle_property_double_click(index: QModelIndex):
            proxy_model: models.SortModel = w.tv_properties.model()
            i = proxy_model.mapToSource(index)
            bsdd_property = i.siblingAtColumn(0).internalPointer()
            cls.signals.property_info_requested.emit(bsdd_property, w)

        def handle_class_double_click(index: QModelIndex):
            proxy_model: models.SortModel = w.tv_classes.model()
            i: QModelIndex = proxy_model.mapToSource(index)
            bsdd_class = i.siblingAtColumn(0).internalPointer()
            cls.signals.bsdd_class_double_clicked.emit(bsdd_class)

        widget.tv_properties.doubleClicked.connect(handle_property_double_click)
        w.tv_classes.doubleClicked.connect(handle_class_double_click)

        widget.tb_new.clicked.connect(lambda _, w=widget: cls.signals.new_property_requested.emit())
        w.tv_properties.customContextMenuRequested.connect(
            lambda p: trigger.context_menu_requested(w.tv_properties, p)
        )

        w.tv_classes.customContextMenuRequested.connect(
            lambda p: trigger.context_menu_requested(w.tv_classes, p)
        )

    @classmethod
    def create_property_model(cls):
        model = models.PropertyTableModel()
        proxy_model = models.SortModel()
        proxy_model.setSourceModel(model)
        proxy_model.setDynamicSortFilter(True)
        cls.get_properties().models.add(model)
        return proxy_model, model

    @classmethod
    def create_class_model(cls):
        model = models.ClassTableModel()
        proxy_model = models.SortModel()
        proxy_model.setSourceModel(model)
        proxy_model.setDynamicSortFilter(True)
        cls.get_properties().models.add(model)
        return proxy_model, model

    @classmethod
    def get_active_property(cls) -> BsddProperty:
        return cls.get_properties().active_property

    @classmethod
    def on_selection_change(cls, view: views.ClassTable | views.PropertyTable, value: BsddProperty):

        def reset_class_views():
            for view in cls.get_views():
                if isinstance(view, views.ClassTable):
                    cls.reset_view(view)

        if isinstance(view, views.PropertyTable):
            cls.get_properties().active_property = value
            cls.signals.active_property_changed.emit(value)
            reset_class_views()
            code = value.Code if value else ""
            widget: ui.PropertyWidget = view.window()
            widget.lb_property_name.setText(code)

    @classmethod
    def select_property(
        cls, bsdd_property: BsddProperty, view: QAbstractItemView | None = None
    ) -> bool:
        """
        Select the given BsddProperty in the properties table and scroll it into view.
        Returns True if the item was found and selected, False otherwise.
        """
        # Determine target view if not provided
        if view is None:
            # Prefer a registered view named 'tv_properties'
            for w in cls.get_widgets():
                try:
                    if hasattr(w, "objectName") and w.objectName() == "tv_properties":
                        view = w  # type: ignore[assignment]
                        break
                except Exception:
                    pass
            if view is None:
                return False

        top_model = view.model()
        if top_model is None:
            return False

        # Unwrap proxy chain to reach the source model
        proxies: list[QSortFilterProxyModel] = []
        model = top_model
        while isinstance(model, QSortFilterProxyModel):
            proxies.append(model)
            model = model.sourceModel()
        source_model = model

        # Linear search in root rows (flat list of properties)
        src_index: QModelIndex | None = None
        row_count = source_model.rowCount() if hasattr(source_model, "rowCount") else 0
        for row in range(row_count):
            idx = source_model.index(row, 0)
            if idx.isValid() and idx.internalPointer() is bsdd_property:
                src_index = idx
                break

        if src_index is None or not src_index.isValid():
            return False

        # Map up through proxies to the view's model
        proxy_index = src_index
        for p in reversed(proxies):
            proxy_index = p.mapFromSource(proxy_index)

        if not proxy_index.isValid():
            return False

        sel_model = view.selectionModel()
        if sel_model is None:
            return False

        # Select, set current, and scroll to center
        sel_model.clearSelection()
        sel_model.setCurrentIndex(proxy_index, QItemSelectionModel.ClearAndSelect)
        sel_model.select(proxy_index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        view.scrollTo(proxy_index, QAbstractItemView.PositionAtCenter)
        return True

    @classmethod
    def request_new_property(cls):
        cls.signals.new_property_requested.emit()
