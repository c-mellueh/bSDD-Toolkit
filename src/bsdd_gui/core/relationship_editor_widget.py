from __future__ import annotations

from typing import TYPE_CHECKING, Type, Literal
from bsdd_parser import BsddProperty, BsddClass
from PySide6.QtWidgets import QWidget, QTreeView
from PySide6.QtCore import QCoreApplication
from bsdd_gui.module.relationship_editor_widget import ui

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.dictionary_editor_widget import ui as ui_dict
    from bsdd_gui.presets.ui_presets import ToggleSwitch


def connect_signals(
    relationship_editor: Type[tool.RelationshipEditorWidget],
    project: Type[tool.Project],
    class_editor: Type[tool.ClassEditorWidget],
):
    project.signals.data_changed.connect(
        lambda n, v: relationship_editor.update_on_dict_change(n, v, project.get())
    )
    project.signals.class_added.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    project.signals.class_removed.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    project.signals.property_added.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    project.signals.property_removed.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    class_editor.signals.dialog_accepted.connect(
        relationship_editor.transform_virtual_relationships_to_real
    )
    relationship_editor.connect_internal_signals()


def retranslate_ui(relationship_editor: Type[tool.RelationshipEditorWidget]):
    for widget in relationship_editor.get_widgets():
        widget.retranslateUi(widget)
        if isinstance(widget.bsdd_data, BsddClass):
            text = QCoreApplication.translate("RelationshipEditor", "Related Class")
        else:
            text = QCoreApplication.translate("RelationshipEditor", "Related Property")
            widget.lb_related_class.setText(text)


def register_view(view: QTreeView, relationship_editor: Type[tool.RelationshipEditorWidget]):
    relationship_editor.register_view(view)


def add_columns_to_view(
    view: QTreeView,
    data: BsddClass | BsddProperty,
    mode: Literal["dialog"] | Literal["live"],
    relationship_editor: Type[tool.RelationshipEditorWidget],
):

    proxy_model, model = relationship_editor.create_model(data)
    model.mode = mode
    if isinstance(data, BsddClass):
        relationship_editor.add_class_columns_to_table(model)
    else:
        relationship_editor.add_property_columns_to_table(model)
    view.setModel(proxy_model)


def add_context_menu_to_view(
    view: QTreeView, relationship_editor: Type[tool.RelationshipEditorWidget]
):
    pass  # TODO:


def connect_view(view: QTreeView, relationship_editor: Type[tool.RelationshipEditorWidget]):
    pass


def remove_view(view: QTreeView, relationship_editor: Type[tool.RelationshipEditorWidget]):
    relationship_editor.unregister_view(view)


def register_widget(
    widget: ui.RelationshipWidget, relationship_editor: Type[tool.RelationshipEditorWidget]
):
    relationship_editor.register_widget(widget)


def connect_widget(
    widget: ui.RelationshipWidget,
    data: BsddClass | BsddProperty,
    mode: Literal["dialog"] | Literal["live"],
    relationship_editor: Type[tool.RelationshipEditorWidget],
    project: Type[tool.Project],
):

    widget.bsdd_data = data
    widget.mode = mode
    relationship_editor.connect_widget_signals(widget, project.get())


def add_field_validators(
    widget: ui.RelationshipWidget,
    relationship_editor: Type[tool.RelationshipEditorWidget],
    util: Type[tool.Util],
    project: Type[tool.Project],
):
    relationship_editor.add_validator(
        widget,
        widget.le_related_element,
        lambda v, w,: relationship_editor.is_related_class_valid(v, w, project.get()),
        lambda w, v: util.set_invalid(w, not v),
    )

    relationship_editor.set_fractions_visible_if_is_material(widget)
    relationship_editor.update_owned_uri_visibility(widget, project.get())
    relationship_editor.update_code_completer(widget, project.get())
    if isinstance(widget.bsdd_data, BsddClass):
        elements = [
            "HasMaterial",
            "HasReference",
            "IsEqualTo",
            "IsSimilarTo",
            "IsParentOf",
            "IsChildOf",
            "HasPart",
            "IsPartOf",
        ]
    else:
        elements = ["HasReference", "IsEqualTo", " IsSimilarTo"]
    widget.cb_relation_type.clear()
    widget.cb_relation_type.addItems(elements)


def remove_widget(
    widget: ui.RelationshipWidget,
    relationship_editor: Type[tool.RelationshipEditorWidget],
):
    relationship_editor.unregister_widget(widget)
