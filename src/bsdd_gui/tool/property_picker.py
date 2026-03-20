
from __future__ import annotations
from typing import TYPE_CHECKING,TypedDict
import logging
from PySide6.QtCore import Signal

import bsdd_gui
from bsdd_json import BsddClass,BsddClassProperty
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.presets.tool_presets import ActionTool,WidgetTool,WidgetSignals,ItemViewTool,ViewSignals
from bsdd_gui.module.property_picker import ui,trigger,model_views,models

if TYPE_CHECKING:
    from bsdd_gui.module.property_picker.prop import PropertyPickerProperties,IdsClassViewProperties,IdsPropertyViewProperties


class PsetDict(TypedDict):
    checked: bool
    proeprties: dict[str, bool]

class Signals(WidgetSignals):
    pass

class PropertyPicker(ActionTool,WidgetTool):
    @classmethod
    def get_properties(cls) -> PropertyPickerProperties:
        return bsdd_gui.PropertyPickerProperties

    @classmethod
    def _get_widget_class(cls) -> type[ui.Widget]:
        return ui.Widget

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def create_widget(cls, *args, **kwargs) -> ui.Widget:
        widget = cls._get_widget_class()(*args, **kwargs)
        cls.add_plugins_to_widget(widget)
        return widget

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()

    @classmethod
    def connect_widget_signals(cls, widget: ui.Widget):
        super().connect_widget_signals(widget)


class ClassSignals(ViewSignals):
    set_inheritance_requested = Signal(bool,model_views.ClassView)


class IdsClassView(ItemViewTool):
    signals = ClassSignals()

    @classmethod
    def get_properties(cls) -> IdsClassViewProperties:
        return bsdd_gui.IdsClassViewProperties  #

    @classmethod
    def _get_model_class(cls):
        return models.ClassTreeModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.SortModel

    @classmethod
    def request_set_inheritance(cls,state:bool,view:model_views.ClassView):
        cls.signals.set_inheritance_requested.emit(state,view)

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.set_inheritance_requested.connect(cls.set_checkstate_inheritance)
        return super().connect_internal_signals()

    @classmethod
    def get_checkstate(cls, bsdd_class: BsddClass):
        return cls.get_properties().checkstate_dict.get(bsdd_class.Code, True)

    @classmethod
    def set_checkstate(cls, bsdd_class: BsddClass, state: bool):
        cls.get_properties().checkstate_dict[bsdd_class.Code] = state

    @classmethod
    def get_check_dict(cls):
        return cls.get_properties().checkstate_dict

    @classmethod
    def set_check_dict(cls, check_dict, treev_view: model_views.ClassView):
        model: models.ClassTreeModel = treev_view.model().sourceModel()
        model.beginResetModel()
        cls.get_properties().checkstate_dict = check_dict
        model.endResetModel()

    @classmethod
    def set_checkstate_inheritance(cls,state:bool,view:model_views.ClassView):
        class_model:models.ClassTreeModel = view.model().sourceModel()
        class_model.set_checkstate_inheritance(state)

class PropertySignals(ViewSignals):
    pass


class IdsPropertyView(ItemViewTool):
    signals = PropertySignals()

    @classmethod
    def get_properties(cls) -> IdsPropertyViewProperties:
        return bsdd_gui.IdsPropertyViewProperties

    @classmethod
    def _get_model_class(cls):
        return models.PropertyTreeModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.SortModel

    @classmethod
    def _get_name(cls, bsdd_property: BsddClassProperty | str):
        if isinstance(bsdd_property, str):
            return bsdd_property
        return prop_utils.get_name(bsdd_property)

    @classmethod
    def _get_code(cls, bsdd_property: BsddClassProperty | str):
        if isinstance(bsdd_property, str):
            return ""
        return bsdd_property.Code

    @classmethod
    def get_checkstate(
        cls, model: models.PropertyTreeModel, bsdd_class_property: BsddClassProperty | str
    ):
        pset_name = (
            bsdd_class_property
            if isinstance(bsdd_class_property, str)
            else bsdd_class_property.PropertySet
        )
        property_code = None if isinstance(bsdd_class_property, str) else bsdd_class_property.Code
        bsdd_class_code = model.bsdd_data.Code
        checkstate_dict: PsetDict = cls.get_properties().checkstate_dict
        class_dict = checkstate_dict.get(bsdd_class_code, None)
        if not class_dict:
            return True
        pset_dict = class_dict.get(pset_name)
        if not pset_dict:
            return True
        if property_code is None:  # propertySet
            return pset_dict.get("checked", True)
        else:
            return pset_dict["properties"].get(property_code, True)

    @classmethod
    def set_checkstate(
        cls,
        model: models.PropertyTreeModel,
        bsdd_class: BsddClass,
        bsdd_class_property: BsddClassProperty | str,
        state: bool,
    ):
        if not model.bsdd_data:
            return

        pset_name = (
            bsdd_class_property
            if isinstance(bsdd_class_property, str)
            else bsdd_class_property.PropertySet
        )
        property_code = None if isinstance(bsdd_class_property, str) else bsdd_class_property.Code
        if bsdd_class.Code not in cls.get_properties().checkstate_dict:
            cls.get_properties().checkstate_dict[bsdd_class.Code] = dict()
        checkstate_dict = cls.get_properties().checkstate_dict[bsdd_class.Code]
        if pset_name not in checkstate_dict:
            checkstate_dict[pset_name] = {"checked": True, "properties": dict()}
        if not property_code:
            checkstate_dict[pset_name]["checked"] = state
        else:
            checkstate_dict[pset_name]["properties"][property_code] = state

    @classmethod
    def get_check_dict(cls):
        return cls.get_properties().checkstate_dict

    @classmethod
    def set_check_dict(cls, check_dict, tree_view: model_views.PropertyView):
        model: models.ClassTreeModel = tree_view.model().sourceModel()
        model.beginResetModel()
        cls.get_properties().checkstate_dict = check_dict
        model.endResetModel()
