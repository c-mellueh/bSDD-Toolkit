from __future__ import annotations
from typing import TYPE_CHECKING, Type
import logging
from types import ModuleType
import bsdd_gui
from PySide6.QtCore import QModelIndex, QObject, Signal, Qt
from bsdd_gui.module.property_set_table_view import ui, models, trigger
from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals, ItemViewTool
from bsdd_json.models import BsddDictionary, BsddClass

if TYPE_CHECKING:
    from bsdd_gui.module.property_set_table_view.prop import PropertySetTableViewProperties


class Signals(ViewSignals):
    new_property_set_requested = Signal(BsddClass)
    delete_selection_requested = Signal(ui.PsetTableView)
    property_set_deleted = Signal(BsddClass, str)
    rename_selection_requested = Signal(ui.PsetTableView)


class PropertySetTableView(ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> PropertySetTableViewProperties:
        return bsdd_gui.PropertySetTableViewProperties

    @classmethod
    def _get_model_class(cls) -> Type[models.PsetTableModel]:
        return models.PsetTableModel

    @classmethod
    def _get_trigger(cls) -> ModuleType:
        return trigger

    @classmethod
    def delete_selection(cls, view: ui.PsetTableView):
        trigger.delete_selection(view)

    @classmethod
    def _get_proxy_model_class(cls) -> Type[models.SortModel]:
        return models.SortModel

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.new_property_set_requested.connect(trigger.new_property_set_requested)
        cls.signals.rename_selection_requested.connect(
            lambda view: view.edit([i for i in view.selectedIndexes() if i.column() == 0][0])
        )

    @classmethod
    def connect_view_signals(cls, view: ui.PsetTableView):
        super().connect_view_signals(view)

    @classmethod
    def create_model(
        cls, bsdd_dictionary: BsddDictionary
    ) -> tuple[models.SortModel | models.ItemModel]:
        return super().create_model(bsdd_dictionary)

    @classmethod
    def on_current_changed(cls, view: ui.PsetTableView, curr: QModelIndex, prev: QModelIndex):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signals.selection_changed.emit(view, index.data(Qt.ItemDataRole.DisplayRole))

    @classmethod
    def request_new_property_set(cls, bsdd_class: BsddClass):
        cls.signals.new_property_set_requested.emit(bsdd_class)

    @classmethod
    def get_pset_names_with_temporary(cls, bsdd_class: BsddClass) -> list[str]:
        bsdd_properties = list()
        if bsdd_class is None:
            return bsdd_properties
        for cp in bsdd_class.ClassProperties:
            if cp.PropertySet not in bsdd_properties:
                bsdd_properties.append(cp.PropertySet)

        if bsdd_class.Code in cls.get_properties().temporary_pset:
            for property_set in cls.get_properties().temporary_pset[bsdd_class.Code]:
                bsdd_properties.append(property_set)
        return bsdd_properties

    @classmethod
    def select_row(cls, view: ui.PsetTableView, row_index: int):
        model = view.model()
        index = model.index(row_index, 0)
        if not index.isValid():
            return
        view.setCurrentIndex(index)

    @classmethod
    def get_row_by_name(cls, view: ui.PsetTableView, name: str):
        model = view.model()
        for row in range(model.rowCount()):
            pset_name = model.index(row, 0).data(Qt.ItemDataRole.DisplayRole)
            if name == pset_name:
                return row
        return None

    @classmethod
    def add_temporary_pset(cls, bsdd_class: BsddClass, name: str):
        class_code = bsdd_class.Code
        if not class_code in cls.get_properties().temporary_pset:
            cls.get_properties().temporary_pset[class_code] = list()
        cls.get_properties().temporary_pset[class_code].append(name)

    @classmethod
    def remove_temporary_pset(cls, bsdd_class: BsddClass, name: str):
        class_code = bsdd_class.Code
        if not class_code in cls.get_properties().temporary_pset:
            cls.get_properties().temporary_pset[class_code] = list()
        if name in cls.get_properties().temporary_pset[class_code]:
            cls.get_properties().temporary_pset[class_code].remove(name)

    @classmethod
    def is_temporary_pset(cls, bsdd_class: BsddClass, name: str) -> bool:
        for prop in bsdd_class.ClassProperties:
            if prop.PropertySet == name:
                return False
        return True

    @classmethod
    def rename_temporary_pset(cls, bsdd_class: BsddClass, old_name, new_name):
        class_code = bsdd_class.Code
        if class_code not in cls.get_properties().temporary_pset:
            return
        if not old_name in cls.get_properties().temporary_pset[class_code]:
            return
        index = cls.get_properties().temporary_pset[class_code].index(old_name)
        cls.get_properties().temporary_pset[class_code][index] = new_name

    @classmethod
    def get_selected(cls, view: ui.PsetTableView):
        return list({index.data() for index in view.selectedIndexes()})

    @classmethod
    def rename_property_set(cls, bsdd_class: BsddClass, old_name, new_name):
        for class_property in bsdd_class.ClassProperties:
            if class_property.PropertySet == old_name:
                class_property.PropertySet = new_name
