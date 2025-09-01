from __future__ import annotations
from typing import TYPE_CHECKING
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
from PySide6.QtWidgets import QWidget, QAbstractItemView
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
    bsdd_class_double_clicked = Signal(object)
    search_requested = Signal(QWidget)


class PropertyTable(ItemModelHandler, ViewHandler, ModuleHandler, WidgetHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyTableProperties:
        return bsdd_gui.PropertyTableProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signaller.widget_requested.connect(lambda _, p: trigger.create_widget(p))
        cls.signaller.widget_created.connect(trigger.widget_created)
        # Only class list depends on the active property; avoid resetting the
        # properties table itself on selection changes to keep keyboard
        # navigation intact.
        cls.signaller.active_property_changed.connect(lambda _: cls.reset_class_views())
        cls.signaller.search_requested.connect(trigger.search_property)

    @classmethod
    def reset_class_views(cls):
        for w in cls.get_widgets():
            # Registered widgets include the container widget and its views.
            # We only want to refresh the classes table when the active
            # property changes.
            try:
                if hasattr(w, "tv_classes"):
                    cls.reset_view(w.tv_classes)
            except Exception:
                pass

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

        def handle_class_double_click(index: QModelIndex):
            proxy_model: models.SortModel = w.tv_classes.model()
            i: QModelIndex = proxy_model.mapToSource(index)
            bsdd_class = i.siblingAtColumn(0).internalPointer()
            cls.signaller.bsdd_class_double_clicked.emit(bsdd_class)

        widget.tv_classes.doubleClicked.connect(handle_class_double_click)

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

    @classmethod
    def select_property(
        cls,
        bsdd_property: BsddProperty,
        view: QAbstractItemView | None = None,
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
