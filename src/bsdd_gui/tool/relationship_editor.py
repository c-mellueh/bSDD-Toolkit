from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import logging

from PySide6.QtWidgets import QTreeView, QCompleter, QWidget
from PySide6.QtCore import Qt
import bsdd_gui
from bsdd_parser import (
    BsddProperty,
    BsddClass,
    BsddDictionary,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_gui.presets.tool_presets import ItemViewHandler, ViewSignals, ItemViewHandler
from bsdd_parser.utils import bsdd_dictionary as dict_util
from bsdd_parser.utils import bsdd_class as cl_util
from bsdd_parser.utils import bsdd_class_property as prop_util
from bsdd_gui.module.class_editor import ui as class_editor_ui

if TYPE_CHECKING:
    from bsdd_gui.module.relationship_editor.prop import RelationshipEditorProperties
from bsdd_gui.module.relationship_editor import ui, trigger, models


class Signaller(ViewSignals):
    pass


class RelationshipEditor(ItemViewHandler):
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
    def connect_widget_signals(cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary):
        w = widget
        widget.closed.connect(lambda: trigger.widget_closed(w))
        widget.cb_fraction.toggled.connect(
            lambda: w.ds_fraction.setEnabled(w.cb_fraction.isChecked())
        )
        widget.cb_relation_type.currentTextChanged.connect(
            lambda _, w=widget: cls.set_fractions_visible_if_is_material(widget)
        )
        widget.cb_relation_type.currentTextChanged.connect(
            lambda _w=widget: cls.update_code_completer(widget, bsdd_dictionary)
        )
        widget.tb_add.clicked.connect(lambda _, w=widget: cls.add_row_to_model(w, bsdd_dictionary))
        widget.le_related_element.returnPressed.connect(
            lambda w=widget: cls.add_row_to_model(w, bsdd_dictionary)
        )

    @classmethod
    def is_related_class_valid(
        cls, value, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary
    ):
        if dict_util.is_uri(value):
            return True
        if isinstance(widget.data, BsddClass):
            element = cl_util.get_class_by_code(bsdd_dictionary, value)
        elif isinstance(widget.data, BsddProperty):
            element = prop_util.get_property_by_code(value, bsdd_dictionary)
        if element is None:
            return False
        if element == widget.data:
            return False
        return True

    @classmethod
    def create_model(cls, data: BsddClass | BsddProperty, mode):
        data_model = models.RelationshipModel(data, mode)
        proxy_model = models.SortModel()
        proxy_model.setSourceModel(data_model)
        return proxy_model

    @classmethod
    def add_class_columns_to_table(cls, model: models.RelationshipModel):
        cls.add_column_to_table(model, "RelationType", lambda cr: cr.RelationType)
        cls.add_column_to_table(model, "RelatedClassUri", lambda cr: cr.RelatedClassUri)
        cls.add_column_to_table(model, "RelatedClassName", lambda cr: cr.RelatedClassName)
        cls.add_column_to_table(model, "Fraction", lambda cr: cr.Fraction)
        cls.add_column_to_table(model, "OwnedUri", lambda cr: cr.OwnedUri)

    @classmethod
    def add_property_columns_to_table(cls, model: models.RelationshipModel):
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

    @classmethod
    def get_widgets(cls) -> set[ui.RelationshipWidget | QTreeView]:
        return super().get_widgets()

    @classmethod
    def update_owned_uri_visibility(
        cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary
    ):
        widget.lb_owned_uri.setVisible(bsdd_dictionary.UseOwnUri)
        widget.le_owned_uri.setVisible(bsdd_dictionary.UseOwnUri)

    @classmethod
    def update_code_completer(
        cls,
        widget: ui.RelationshipWidget,
        bsdd_dictionary: BsddDictionary,
    ):
        if isinstance(widget.data, BsddClass):
            codes = [c.Code for c in bsdd_dictionary.Classes]
            if widget.cb_relation_type.currentText() == "HasMaterial":
                codes = [c.Code for c in bsdd_dictionary.Classes if c.ClassType == "Material"]
            else:
                codes = [c.Code for c in bsdd_dictionary.Classes]
            completer = QCompleter(codes)
        else:
            codes = [c.Code for c in bsdd_dictionary.Properties]
            completer = QCompleter(codes)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        widget.le_related_element.setCompleter(completer)

    @classmethod
    def update_on_dict_change(cls, field_name, value, bsdd_dictionary: BsddDictionary):
        if field_name == "UseOwnUri":
            for widget in cls.get_widgets():
                if not isinstance(widget, ui.RelationshipWidget):
                    continue
                cls.update_owned_uri_visibility(widget, bsdd_dictionary)
        if field_name in ["DictionaryVersion", "OrganizationCode", "DictionaryCode"]:
            for cl in bsdd_dictionary.Classes:
                cl_util.update_relations_to_new_uri(cl, bsdd_dictionary)
            for prop in bsdd_dictionary.Properties:
                prop_util.update_relations_to_new_uri(prop, bsdd_dictionary)

    @classmethod
    def update_all_completers(cls, bsdd_dictionary: BsddDictionary):
        for widget in cls.get_widgets():
            if not isinstance(widget, ui.RelationshipWidget):
                continue
            cls.update_code_completer(widget, bsdd_dictionary)

    @classmethod
    def add_row_to_model(cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary):
        def clear_inputs():
            widget.le_owned_uri.clear()
            widget.le_related_element.clear()
            widget.ds_fraction.clear()

        model = widget.tv_relations.model().sourceModel()
        model: models.RelationshipModel
        model_kind = "class" if isinstance(model.item_data, BsddClass) else "property"
        data_dict = {"RelationType": widget.cb_relation_type.currentText()}
        if bsdd_dictionary.UseOwnUri and widget.le_owned_uri.text():
            data_dict["OwnedUri"] = widget.le_owned_uri.text()

        if model_kind == "class":
            code = widget.le_related_element.text()
            related_class = cl_util.get_class_by_code(bsdd_dictionary, code)
            if not related_class:
                clear_inputs()
                return
            if dict_util.is_uri(code):
                data_dict["RelatedClassUri"] = code
            else:
                data_dict["RelatedClassUri"] = cl_util.build_bsdd_uri(
                    related_class, bsdd_dictionary
                )
            data_dict["RelatedClassName"] = related_class.Name

            if (
                widget.cb_fraction.isChecked()
                and widget.cb_relation_type.currentText() == "HasMaterial"
            ):
                data_dict["Fraction"] = widget.ds_fraction.value()
            relation = BsddClassRelation.model_validate(data_dict)
        else:
            code = widget.le_related_element.text()
            related_property = prop_util.get_property_by_code(code, bsdd_dictionary)
            if not related_property:
                clear_inputs()
                return
            if dict_util.is_uri(code):
                data_dict["RelatedPropertyUri"] = code
            else:
                data_dict["RelatedPropertyUri"] = prop_util.build_bsdd_uri(
                    related_property, bsdd_dictionary
                )
            data_dict["RelatedPropertyName"] = related_property.Name
            relation = BsddPropertyRelation.model_validate(data_dict)

        if model.mode == "dialog":
            model.append_row(relation)
        else:
            model.append_row(relation)
        clear_inputs()

    @classmethod
    def transform_virtual_relationships_to_real(cls, widget: QWidget):
        if isinstance(widget, class_editor_ui.ClassEditor):
            table_view = widget.relationship_editor.tv_relations
            model: models.RelationshipModel = table_view.model().sourceModel()
            model.beginResetModel()
            for relationship in list(model.virtual_remove):
                if isinstance(model.item_data, BsddClass):
                    model.item_data.ClassRelations.remove(relationship)  # type: ignore[arg-type]
                else:
                    model.item_data.PropertyRelations.remove(relationship)  # type: ignore[arg-type]
                model.virtual_remove.remove(relationship)

            for relationship in list(model.virtual_append):
                if isinstance(model.item_data, BsddClass):
                    model.item_data.ClassRelations.append(relationship)  # type: ignore[arg-type]
                else:
                    model.item_data.PropertyRelations.append(relationship)  # type: ignore[arg-type]
                model.virtual_append.remove(relationship)
            model.endResetModel()
