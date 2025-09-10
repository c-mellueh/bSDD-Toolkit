from __future__ import annotations

from typing import TYPE_CHECKING, Type, Literal
from bsdd_json import BsddProperty, BsddClass, BsddClassRelation, BsddPropertyRelation
from PySide6.QtWidgets import QWidget, QTableView
from PySide6.QtCore import QCoreApplication, QPoint
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
        relationship_editor.transform_virtual_relations_to_real
    )
    relationship_editor.connect_internal_signals()

    def handle_item_remove(item):
        if isinstance(item, BsddClassRelation):
            project.signals.class_relation_removed.emit(item)
        elif isinstance(item, BsddPropertyRelation):
            project.signals.property_relation_removed.emit(item)

    def handle_item_add(item):
        if isinstance(item, BsddClassRelation):
            project.signals.class_relation_added.emit(item)
        elif isinstance(item, BsddPropertyRelation):
            project.signals.property_relation_added.emit(item)

    relationship_editor.signals.item_added.connect(handle_item_add)
    relationship_editor.signals.item_removed.connect(handle_item_remove)

    relationship_editor.signals.class_relation_added.connect(project.signals.class_relation_added)
    relationship_editor.signals.class_relation_removed.connect(
        project.signals.class_relation_removed
    )
    relationship_editor.signals.property_relation_added.connect(
        project.signals.property_relation_added
    )
    relationship_editor.signals.property_relation_removed.connect(
        project.signals.property_relation_removed
    )

    project.signals.class_relation_added.connect(
        lambda r: relationship_editor.make_class_relation_bidrectional(r, project.get(),mode = "add")
    )

    project.signals.class_relation_removed.connect(
        lambda r: relationship_editor.make_class_relation_bidrectional(r, project.get(),mode = "remove")
    )

    project.signals.class_relation_added.connect(print)


def retranslate_ui(relationship_editor: Type[tool.RelationshipEditorWidget]):
    for widget in relationship_editor.get_widgets():
        widget.retranslateUi(widget)
        if isinstance(widget.bsdd_data, BsddClass):
            text = QCoreApplication.translate("RelationshipEditor", "Related Class")
        else:
            text = QCoreApplication.translate("RelationshipEditor", "Related Property")
            widget.lb_related_class.setText(text)


def register_widget(
    widget: ui.RelationshipWidget,
    data: BsddClass | BsddProperty,
    relationship_editor: Type[tool.RelationshipEditorWidget],
):
    widget.bsdd_data = data
    relationship_editor.register_widget(widget)


def register_view(view: QTableView, relationship_editor: Type[tool.RelationshipEditorWidget]):
    relationship_editor.register_view(view)


def add_columns_to_view(
    view: QTableView,
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
    view: QTableView, relationship_editor: Type[tool.RelationshipEditorWidget]
):
    relationship_editor.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("AllowedValuesTable", "Delete"),
        lambda: relationship_editor.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )


def create_context_menu(
    view: QTableView, pos: QPoint, relationship_editor: Type[tool.RelationshipEditorWidget]
):
    bsdd_allowed_values = relationship_editor.get_selected(view)
    menu = relationship_editor.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def connect_view(view: QTableView, relationship_editor: Type[tool.RelationshipEditorWidget]):
    relationship_editor.connect_view_signals(view)


def remove_view(view: QTableView, relationship_editor: Type[tool.RelationshipEditorWidget]):
    relationship_editor.unregister_view(view)


def register_fields(
    widget: ui.RelationshipWidget, relationship_editor: Type[tool.RelationshipEditorWidget]
):
    return


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


def register_validators(
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
    widget: ui.RelationshipWidget, relationship_editor: Type[tool.RelationshipEditorWidget]
):
    relationship_editor.unregister_widget(widget)
