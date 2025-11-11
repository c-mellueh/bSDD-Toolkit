from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Type
import logging

from PySide6.QtWidgets import QTreeView, QCompleter, QTableView
from PySide6.QtCore import Qt, Signal
import bsdd_gui
from bsdd_json import (
    BsddProperty,
    BsddClass,
    BsddDictionary,
    BsddClassRelation,
    BsddPropertyRelation,
)
from bsdd_gui.presets.tool_presets import ItemViewTool, ViewSignals, FieldTool, FieldSignals
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.module.class_editor_widget import ui as class_editor_ui
from bsdd_gui.presets.ui_presets import BaseDialog

if TYPE_CHECKING:
    from bsdd_gui.module.relationship_editor_widget.prop import RelationshipEditorWidgetProperties
from bsdd_gui.module.relationship_editor_widget import ui, trigger, models


class Signals(ViewSignals, FieldSignals):
    class_relation_added = Signal(BsddClassRelation)
    class_relation_removed = Signal(BsddClassRelation)

    property_relation_added = Signal(BsddPropertyRelation)
    property_relation_removed = Signal(BsddPropertyRelation)


class RelationshipEditorWidget(FieldTool, ItemViewTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> RelationshipEditorWidgetProperties:
        return bsdd_gui.RelationshipEditorWidgetProperties

    @classmethod
    def _get_model_class(cls) -> Type[models.RelationshipModel]:
        return models.RelationshipModel

    @classmethod
    def _get_proxy_model_class(cls) -> Type[models.SortModel]:
        return models.SortModel

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def delete_selection(view: QTreeView):
        # TODO
        return None

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
    def init_widget(
        cls,
        widget: ui.RelationshipWidget,
        data: BsddProperty | BsddClass,
        mode: Literal["dialog"] | Literal["live"] = "dialog",
    ):
        trigger.widget_created(widget, data, mode)

    @classmethod
    def connect_widget_signals(cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary):
        super().connect_widget_signals(widget)
        w = widget
        widget.closed.connect(lambda: cls.unregister_view(w.tv_relations))

        widget.cb_fraction.toggled.connect(
            lambda: w.ds_fraction.setEnabled(w.cb_fraction.isChecked())
        )
        widget.cb_relation_type.currentTextChanged.connect(
            lambda _, w=widget: cls.set_fractions_visible_if_is_material(widget)
        )
        widget.cb_relation_type.currentTextChanged.connect(
            lambda _w=widget: cls.update_code_completer(widget, bsdd_dictionary)
        )
        widget.tb_add.clicked.connect(
            lambda _, w=widget: cls.add_relation_to_model(w, bsdd_dictionary)
        )
        widget.le_related_element.returnPressed.connect(
            lambda w=widget: cls.add_relation_to_model(w, bsdd_dictionary)
        )

    @classmethod
    def is_related_class_valid(
        cls, value, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary
    ):
        if dict_utils.is_uri(value):
            return True
        if isinstance(widget.bsdd_data, BsddClass):
            element = cl_utils.get_class_by_code(bsdd_dictionary, value)
        elif isinstance(widget.bsdd_data, BsddProperty):
            element = prop_utils.get_property_by_code(value, bsdd_dictionary)
        if element is None:
            return False
        if element == widget.bsdd_data:
            return False
        return True

    @classmethod
    def set_fractions_visible_if_is_material(cls, widget: ui.RelationshipWidget):
        visible = widget.cb_relation_type.currentText() == "HasMaterial"

        widget.cb_fraction.setVisible(visible)
        widget.lb_fraction.setVisible(visible)
        widget.ds_fraction.setVisible(visible)

    @classmethod
    def get_widgets(cls) -> set[ui.RelationshipWidget]:
        return super().get_widgets()

    @classmethod
    def update_owned_uri_visibility(
        cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary
    ):
        widget.lb_owned_uri.setVisible(bsdd_dictionary.UseOwnUri)
        widget.le_owned_uri.setVisible(bsdd_dictionary.UseOwnUri)

    @classmethod
    def update_code_completer(cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary):
        if isinstance(widget.bsdd_data, BsddClass):
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
                cl_utils.update_internal_relations_to_new_version(cl, bsdd_dictionary)
            for prop in bsdd_dictionary.Properties:
                prop_utils.update_internal_relations_to_new_version(prop, bsdd_dictionary)

    @classmethod
    def update_all_completers(cls, bsdd_dictionary: BsddDictionary):
        for widget in cls.get_widgets():
            if not isinstance(widget, ui.RelationshipWidget):
                continue
            cls.update_code_completer(widget, bsdd_dictionary)

    @classmethod
    def add_relation_to_model(cls, widget: ui.RelationshipWidget, bsdd_dictionary: BsddDictionary):
        def clear_inputs():
            widget.le_owned_uri.clear()
            widget.le_related_element.clear()
            widget.ds_fraction.clear()

        model = widget.tv_relations.model().sourceModel()
        model: models.RelationshipModel
        model_kind = "class" if isinstance(model.bsdd_data, BsddClass) else "property"
        data_dict = {"RelationType": widget.cb_relation_type.currentText()}
        if bsdd_dictionary.UseOwnUri and widget.le_owned_uri.text():
            data_dict["OwnedUri"] = widget.le_owned_uri.text()

        if model_kind == "class":
            code = widget.le_related_element.text()
            related_class = cl_utils.get_class_by_code(bsdd_dictionary, code)
            if not related_class:
                clear_inputs()
                return
            if dict_utils.is_uri(code):
                data_dict["RelatedClassUri"] = code
            else:
                data_dict["RelatedClassUri"] = cl_utils.build_bsdd_uri(
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
            related_property = prop_utils.get_property_by_code(code, bsdd_dictionary)
            if not related_property:
                clear_inputs()
                return
            if dict_utils.is_uri(code):
                data_dict["RelatedPropertyUri"] = code
            else:
                data_dict["RelatedPropertyUri"] = prop_utils.build_bsdd_uri(
                    related_property, bsdd_dictionary
                )
            data_dict["RelatedPropertyName"] = related_property.Name
            relation = BsddPropertyRelation.model_validate(data_dict)
        model.append_relation(relation)
        if model.mode == "live":
            cls.signals.item_added.emit(relation)
        clear_inputs()

    @classmethod
    def delete_selection(cls, view: QTableView):
        model: models.RelationshipModel = view.model().sourceModel()
        for relation in cls.get_selected(view):
            model.remove_relation(relation)
            if model.mode == "live":
                cls.signals.item_removed.emit(relation)

    @classmethod
    def transform_virtual_relations_to_real(cls, dialog: BaseDialog):
        widget = dialog._widget
        if isinstance(widget, class_editor_ui.ClassEditor):
            table_view = widget.relationship_editor.tv_relations
            model: models.RelationshipModel = table_view.model().sourceModel()
            model.beginResetModel()
            for relation in list(model.virtual_remove):
                if isinstance(model.bsdd_data, BsddClass):
                    model.bsdd_data.ClassRelations.remove(relation)  # type: ignore[arg-type]
                else:
                    model.bsdd_data.PropertyRelations.remove(relation)  # type: ignore[arg-type]
                cls.signals.item_removed.emit(relation)

                model.virtual_remove.remove(relation)

            for relation in list(model.virtual_append):
                if isinstance(model.bsdd_data, BsddClass):
                    model.bsdd_data.ClassRelations.append(relation)  # type: ignore[arg-type]
                else:
                    model.bsdd_data.PropertyRelations.append(relation)  # type: ignore[arg-type]
                cls.signals.item_added.emit(relation)

                model.virtual_append.remove(relation)
            model.endResetModel()

    @classmethod
    def get_widget(cls, bsdd_data: BsddClass | BsddProperty) -> ui.RelationshipWidget:
        return super().get_widget(bsdd_data)

    @classmethod
    def read_relation(
        cls, relation: BsddClassRelation | BsddPropertyRelation, bsdd_dictionary: BsddDictionary
    ):
        start_data = relation._parent_ref()
        relation_type = relation.RelationType

        if isinstance(relation, BsddClassRelation):
            related_uri = relation.RelatedClassUri
            code = dict_utils.parse_bsdd_url(related_uri).get("resource_id")
            end_data = cl_utils.get_class_by_code(bsdd_dictionary, code)

        elif isinstance(relation, BsddPropertyRelation):
            related_uri = relation.RelatedPropertyUri
            code = dict_utils.parse_bsdd_url(related_uri).get("resource_id")
            end_data = prop_utils.get_property_by_code(code)
        return start_data, end_data, relation_type

    @classmethod
    def make_class_relation_bidirectional(
        cls,
        relation: BsddClassRelation,
        bsdd_dictionary: BsddDictionary,
        mode: Literal["add"] | Literal["remove"] = "add",
    ):
        start_class, end_class, relation_type = cls.read_relation(relation, bsdd_dictionary)
        start_uri = cl_utils.build_bsdd_uri(start_class, bsdd_dictionary)

        inverse_relations = {
            "IsChildOf": "IsParentOf",
            "HasPart": "IsPartOf",
            "IsEqualTo": "IsEqualTo",
        }
        for k, v in dict(inverse_relations).items():
            inverse_relations[v] = k

        if relation_type not in inverse_relations:
            return

        relation_found = False
        for cr in end_class.ClassRelations:
            if (
                cr.RelatedClassUri == start_uri
                and cr.RelationType == inverse_relations[relation_type]
            ):
                relation_found = True
        if relation_found and mode == "add":
            return
        if not relation_found and mode == "remove":
            return
        end_type = inverse_relations.get(relation_type)
        if mode == "add":
            rel = BsddClassRelation(
                RelationType=end_type,
                RelatedClassUri=start_uri,
                RelatedClassName=start_class.Name,
            )
            rel._set_parent(end_class)
            end_class.ClassRelations.append(rel)
            cls.signals.class_relation_added.emit(rel)
        elif mode == "remove":
            for cr in list(end_class.ClassRelations):
                if cr.RelatedClassUri == start_uri and cr.RelationType == end_type:
                    end_class.ClassRelations.remove(cr)
                    cls.signals.class_relation_removed.emit(cr)
