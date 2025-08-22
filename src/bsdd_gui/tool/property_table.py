from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from PySide6.QtCore import QModelIndex,QObject,Signal,Qt

import bsdd_gui
from bsdd_parser.models import BsddClassProperty,BsddClass
from bsdd_parser.utils import bsdd_class_property as cp_utils

from bsdd_gui.module.property_table import ui,models,data
from bsdd_gui.presets.tool_presets import ColumnHandler,ViewHandler,ViewSignaller

if TYPE_CHECKING:
    from bsdd_gui.module.property_table.prop import PropertyTableProperties

class Signaller(ViewSignaller):
    pass

class PropertyTable(ColumnHandler,ViewHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> PropertyTableProperties:
        return bsdd_gui.PropertyTableProperties

    @classmethod
    def create_model(cls):
        model = models.PropertyTableModel()
        sort_filter_model = models.SortModel()
        sort_filter_model.setSourceModel(model)
        return sort_filter_model

    @classmethod
    def on_current_changed(cls,view:ui.PropertyTable,curr:QModelIndex, prev):
        proxy_model = view.model()
        if not curr.isValid():
            return
        index = proxy_model.mapToSource(curr)
        cls.signaller.selection_changed.emit(view,index.internalPointer())

    @classmethod
    def filter_properties_by_pset(cls, bsdd_class: BsddClass, pset_name: str):
        return [p for p in bsdd_class.ClassProperties if p.PropertySet == pset_name]

    @classmethod
    def get_datatype(cls,class_property:BsddClassProperty):
        if not cp_utils.is_external_ref(class_property):
            bsdd_property = cp_utils.get_internal_property(class_property)
            return bsdd_property.DataType
        
        external_property = data.PropertyData.get_external_property(class_property)
        if external_property is None:
            return ""
        return external_property.get("dataType") or ''
    
    @classmethod
    def get_units(cls,class_property:BsddClassProperty):
        if not cp_utils.is_external_ref(class_property):
            bsdd_property = cp_utils.get_internal_property(class_property)
            return bsdd_property.Units
        
        external_property = data.PropertyData.get_external_property(class_property)
        if external_property is None:
            return []
        return external_property.get("Units") or []
    
    @classmethod
    def get_allowed_values(cls,class_property:BsddClassProperty):
        return [v.Code for v in class_property.AllowedValues]
    