from __future__ import annotations
from typing import TYPE_CHECKING, Type
import logging
from types import ModuleType
import bsdd_gui
from PySide6.QtCore import QModelIndex, Signal, Qt, QCoreApplication
from PySide6.QtWidgets import QComboBox
from bsdd_gui.module.property_set_table_view import ui, models, trigger
from bsdd_gui.presets.tool_presets import ViewSignals, ItemViewTool
from bsdd_json.models import BsddDictionary, BsddClass, BsddClassRelation
from bsdd_json.utils import class_utils

if TYPE_CHECKING:
    from bsdd_gui.module.property_set_table_view.prop import (
        PropertySetTableViewProperties,
    )


class Signals(ViewSignals):
    new_property_set_requested = Signal(BsddClass)
    delete_selection_requested = Signal(ui.PsetTableView)
    property_set_deleted = Signal(BsddClass, str)
    rename_selection_requested = Signal(ui.PsetTableView)
    property_set_added = Signal(str)
    data_changed = Signal(QModelIndex, QModelIndex, list)


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
        cls.signals.property_set_added.connect(lambda _: cls.signals.model_refresh_requested.emit())

    @classmethod
    def connect_view_signals(cls, view: ui.PsetTableView):
        super().connect_view_signals(view)

    @classmethod
    def create_model(
        cls, bsdd_dictionary: BsddDictionary
    ) -> tuple[models.SortModel, models.ItemModel]:
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
    def get_temporary_psets(cls, bsdd_class: BsddClass):
        if bsdd_class.Code in cls.get_properties().temporary_pset:
            return cls.get_properties().temporary_pset[bsdd_class.Code]
        return []

    @classmethod
    def get_pset_names_with_temporary(cls, bsdd_class: BsddClass) -> list[str]:
        bsdd_properties = list()
        if bsdd_class is None:
            return bsdd_properties
        for cp in bsdd_class.ClassProperties:
            if cp.PropertySet not in bsdd_properties:
                bsdd_properties.append(cp.PropertySet)

        temporary_psets = cls.get_temporary_psets(bsdd_class)
        return bsdd_properties + temporary_psets

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
        if class_code not in cls.get_properties().temporary_pset:
            cls.get_properties().temporary_pset[class_code] = list()
        cls.get_properties().temporary_pset[class_code].append(name)

    @classmethod
    def remove_temporary_pset(cls, bsdd_class: BsddClass, name: str):
        class_code = bsdd_class.Code
        if class_code not in cls.get_properties().temporary_pset:
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
        if old_name not in cls.get_properties().temporary_pset[class_code]:
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

    @classmethod
    def set_combobox(cls, value: QComboBox):
        cls.get_properties().combo_box = value

    @classmethod
    def get_combobox(cls) -> QComboBox:
        return cls.get_properties().combo_box

    @classmethod
    def get_name_from_combobox(cls):
        return cls.get_combobox().currentText()

    @classmethod
    def is_pset_predefined(cls, pset_name: str, bsdd_dictionary: BsddDictionary):
        return pset_name in [
            c.Name for c in bsdd_dictionary.Classes if c.ClassType == "GroupOfProperties"
        ]

    @classmethod
    def is_pset_existing(cls, pset_name, bsdd_class: BsddClass):
        return pset_name in cls.get_pset_names_with_temporary(bsdd_class)

    @classmethod
    def create_connected_pset(
        cls, pset_name: str, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary
    ):
        pset_classes = [c for c in bsdd_dictionary.Classes if c.Name == pset_name]
        if not pset_classes:
            return
        if len(pset_classes) > 1:
            logging.warning(f"Multiple Pset Classes found! for {pset_name}")
            # TODO: Add a Picker or disalow multiple Psets with the same name
        pset_class = pset_classes[0]
        existing_codes = {cp.Code: cp for cp in bsdd_class.ClassProperties}
        warning_text = QCoreApplication.translate(
            "PropertySet",
            "There exists allready a ClassProperty with the Code '{}' in the PropertySet '{}'",
        )

        for cp in pset_class.ClassProperties:
            if cp.Code in existing_codes:
                logging.warning(
                    warning_text.format(cp.Code, existing_codes.get(cp.Code).PropertySet)
                )
                continue
            new_cp = cp.model_copy(deep=True)

            bsdd_class.ClassProperties.append(new_cp)
            new_cp._set_parent(bsdd_class)
            existing_codes[new_cp.Code] = new_cp

        if len([cp for cp in bsdd_class.ClassProperties if cp.PropertySet == pset_name]) == 0:
            cls.add_temporary_pset(bsdd_class, pset_name)
        cls.add_pset_relation(bsdd_class, pset_class, bsdd_dictionary)

    @classmethod
    def add_pset_relation(
        cls, bsdd_class: BsddClass, pset_class: BsddClass, bsdd_dictionary: BsddDictionary
    ):
        uri = class_utils.build_bsdd_uri(pset_class, bsdd_dictionary)
        relation = BsddClassRelation(
            RelationType="HasReference", RelatedClassUri=uri, RelatedClassName=pset_class.Name
        )
        bsdd_class.ClassRelations.append(relation)

    @classmethod
    def get_related_psets(
        cls, bsdd_class: BsddClass, bsdd_dictionary: BsddDictionary
    ) -> list[BsddClass]:
        related_psets = list()

        for cr in bsdd_class.ClassRelations:
            if cr.RelationType != "HasReference":
                continue
            uri = cr.RelatedClassUri
            related_class = class_utils.get_class_by_uri(bsdd_dictionary, uri)
            if not related_class:
                continue
            if related_class.ClassType == "GroupOfProperties":
                related_psets.append(related_class)
        return related_psets
