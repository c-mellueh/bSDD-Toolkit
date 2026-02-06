from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
import bsdd_gui
from bsdd_gui.presets.tool_presets import (
    FieldTool,
    ActionTool,
    ItemViewTool,
    FieldSignals,
    ViewSignals,
)
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils
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
    active_class_changed = Signal(BsddClass)
    active_property_changed = Signal(BsddClassProperty)


class GroupOfProperties(FieldTool, ActionTool):
    signals = WidgetSignals()

    @classmethod
    def get_properties(cls) -> GroupOfPropertiesProperties:
        return bsdd_gui.GroupOfPropertiesProperties

    @classmethod
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.active_class_changed.connect(lambda *_: cls.update_class_label())
        cls.signals.active_class_changed.connect(lambda *_: cls.update_property_enabled_state())
        cls.signals.active_property_changed.connect(lambda *_: cls.update_property_label())

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
    def set_active_class(cls, bsdd_class: BsddClass):
        cls.get_properties().active_class = bsdd_class
        cls.signals.active_class_changed.emit(bsdd_class)

    @classmethod
    def get_active_class(cls) -> BsddClass:
        return cls.get_properties().active_class

    @classmethod
    def set_active_property(cls, value: BsddClassProperty):
        cls.get_properties().active_class_property = value
        cls.signals.active_property_changed.emit(value)

    @classmethod
    def update_property_enabled_state(cls):
        widget = cls.get_widget()
        if not widget:
            return
        widget.glw_property.setEnabled(cls.get_active_class() is not None)

    @classmethod
    def update_class_label(cls):
        widget = cls.get_widget()
        widget.lb_class
        active_class = cls.get_active_class()
        text = QCoreApplication.translate("GroupOfProperties", "Group of properties: {}")
        text = text.format(active_class.Name if active_class else "")
        widget.lb_class.setText(text)

    @classmethod
    def update_property_label(cls):
        widget = cls.get_widget()
        widget.lb_class
        active_property = cls.get_active_property()
        text = QCoreApplication.translate("GroupOfProperties", "Property: {}")
        text = text.format(active_property.Code if active_property else "")
        widget.lb_prop.setText(text)

    @classmethod
    def get_active_property(cls) -> BsddClassProperty:
        return cls.get_properties().active_class_property

    @classmethod
    def generate_pset_name(cls, bsdd_class: BsddClass):
        if bsdd_class is None:
            return ""
        return bsdd_class.Name

    @classmethod
    def get_widget(cls, data=None) -> ui.GopWidget:
        widgets = cls.get_properties().widgets
        if not widgets:
            return None
        return widgets[-1]

    @classmethod
    def reset_property(cls, active_class: BsddClass):
        """
        if the class changes this function checks if the new class has a propertySet with the same name as the old class and selects it
        """

        active_prop = cls.get_active_property()

        if active_prop is None:
            return
        view = cls.get_widget().tv_properties
        if not active_class:
            return
        code_dict = {p.Code: p for p in active_class.ClassProperties}
        if active_prop.Code in code_dict:
            new_property = code_dict[active_prop.Code]
            row_index = GopPropertyView.get_row_of_property(view, new_property)
            cls.set_active_property(new_property)

        else:
            row_index = 0
            cls.set_active_property(None)

        GopPropertyView.select_row(view, row_index or 0)

    @classmethod
    def get_related_classes(
        cls, group_of_properties: BsddClass, bsdd_dictionary: BsddDictionary
    ) -> list[BsddClass]:
        uri = class_utils.build_bsdd_uri(group_of_properties, bsdd_dictionary)
        classes = list()
        for bsdd_class in bsdd_dictionary.Classes:
            for relation in bsdd_class.ClassRelations:
                if relation.RelationType != "HasReference":
                    continue
                if relation.RelatedClassUri == uri:
                    classes.append(bsdd_class)
        return classes

    @classmethod
    def update_code_of_relating_classes(
        cls, gop_property: BsddClassProperty, new_code: str, bsdd_dictionary: BsddDictionary
    ):
        relating_properties = prop_utils.get_relating_properties(gop_property, bsdd_dictionary)
        for prop in relating_properties:
            prop.Code = new_code


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
    def connect_internal_signals(cls):
        super().connect_internal_signals()
        cls.signals.item_added.connect(trigger.add_class_property_to_linked)
        cls.signals.item_removed.connect(trigger.remove_class_property_from_linked)

    @classmethod
    def _get_model_class(cls):
        return models.PropertyTableModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def _get_proxy_model_class(cls):
        return models.PropertySortModel

    @classmethod
    def request_new_property(cls):
        from bsdd_gui import tool

        bsdd_class = tool.GroupOfProperties.get_active_class()
        property_set = tool.GroupOfProperties.generate_pset_name(bsdd_class)
        cls.signals.new_property_requested.emit(bsdd_class, property_set)

    @classmethod
    def sync_allowed_values(cls, view: views.GopPropertyView, bsdd_dictionary: BsddDictionary):
        for bsdd_property in cls.get_selected(view):
            bsdd_property: BsddClassProperty
            bsdd_class = bsdd_property.parent()
            if not bsdd_class or bsdd_class.ClassType != "GroupOfProperties":
                return
            relating_properties = prop_utils.get_relating_properties(bsdd_property, bsdd_dictionary)
            for rp in relating_properties:
                rp.AllowedValues = [av.model_copy(deep=True) for av in bsdd_property.AllowedValues]
