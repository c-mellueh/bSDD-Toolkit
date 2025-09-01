from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import logging


import bsdd_gui
from bsdd_parser import BsddProperty, BsddClass, BsddDictionary
from bsdd_gui.presets.tool_presets import ViewHandler, ViewSignaller, ItemModelHandler
from bsdd_parser.utils import bsdd_dictionary as dict_utils
from bsdd_parser.utils import bsdd_class as cl_utils
from bsdd_parser.utils import bsdd_class_property as prop_utils

if TYPE_CHECKING:
    from bsdd_gui.module.relationship_editor.prop import RelationshipEditorProperties
from bsdd_gui.module.relationship_editor import ui, trigger, models


class Signaller(ViewSignaller):
    pass


class RelationshipEditor(ViewHandler, ItemModelHandler):
    signaller = Signaller()

    @classmethod
    def get_properties(cls) -> RelationshipEditorProperties:
        return bsdd_gui.RelationshipEditorProperties

    @classmethod
    def init_widget(
        cls,
        widget: ui.RelationshipWidget,
        data: BsddProperty | BsddClass,
        mode: Literal["dialog"] | Literal["live"] = "dialog",
    ):
        trigger.widget_created(widget, data, mode)

    @classmethod
    def connect_internal_signals(cls):
        pass

    @classmethod
    def connect_widget_signals(cls, widget: ui.RelationshipWidget):
        w = widget
        widget.closed.connect(lambda: trigger.widget_closed(w))
        widget.cb_fraction.toggled.connect(
            lambda: w.ds_fraction.setEnabled(w.cb_fraction.isChecked())
        )
        widget.cb_relation_type.currentTextChanged.connect(
            lambda _, w=widget: cls.set_fractions_visible_if_is_material(widget)
        )

    @classmethod
    def is_related_class_valid(
        cls, value, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary
    ):
        if dict_utils.is_uri(value):
            return True
        if isinstance(widget.data, BsddClass):
            element = cl_utils.get_class_by_code(bsdd_dictionary, value)
        elif isinstance(widget.data, BsddProperty):
            element = prop_utils.get_property_by_code(value, bsdd_dictionary)
        if element is None:
            return False
        if element == widget.data:
            return False
        return True

    @classmethod
    def create_model(cls, data: BsddClass | BsddProperty, mode):
        model = models.ClassModel if isinstance(data, BsddClass) else models.PropertyModel
        data_model = model(data, mode)
        proxy_model = models.SortModel()
        proxy_model.setSourceModel(data_model)
        return proxy_model

    @classmethod
    def add_class_columns_to_table(cls, model: models.ClassModel):
        cls.add_column_to_table(model, "RelationType", lambda cr: cr.RelationType)
        cls.add_column_to_table(model, "RelatedClassUri", lambda cr: cr.RelatedClassUri)
        cls.add_column_to_table(model, "RelatedClassName", lambda cr: cr.RelatedClassName)
        cls.add_column_to_table(model, "Fraction", lambda cr: cr.Fraction)
        cls.add_column_to_table(model, "OwnedUri", lambda cr: cr.OwnedUri)

    @classmethod
    def add_property_columns_to_table(cls, model: models.PropertyModel):
        cls.add_column_to_table(model, "RelationType", lambda cr: cr.RelationType)
        cls.add_column_to_table(model, "RelatedPropertyUri", lambda cr: cr.RelatedPropertyUri)
        cls.add_column_to_table(model, "RelatedPropertyName", lambda cr: cr.RelatedPropertyName)
        cls.add_column_to_table(model, "OwnedUri", lambda cr: cr.OwnedUri)

    @classmethod
    def set_fractions_visible_if_is_material(cls, widget: ui.RelationshipWidget):
        visible = widget.cb_relation_type.currentText() == "HasMaterial"

        widget.cb_fraction.setVisible(visible)
        widget.lb_fraction.setVisible(visible)
        widget.ds_fraction.setVisible(visible)
