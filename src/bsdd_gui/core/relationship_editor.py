from __future__ import annotations

from typing import TYPE_CHECKING, Type, Literal
from bsdd_parser import BsddProperty, BsddClass
from PySide6.QtWidgets import QWidget


if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.relationship_editor import ui
    from bsdd_gui.module.dictionary_editor import ui as ui_dict
    from bsdd_gui.presets.ui_presets import ToggleSwitch


def connect_widget(
    widget: ui.RelationshipWidget,
    data: BsddClass | BsddProperty,
    mode: Literal["dialog"] | Literal["live"],
    relationship_editor: Type[tool.RelationshipEditor],
    project: Type[tool.Project],
):

    relationship_editor.register_widget(widget)
    relationship_editor.register_widget(widget.tv_relations)
    widget.data = data
    widget.mode = mode
    relationship_editor.connect_widget_signals(widget, project.get())
    proxy_model = relationship_editor.create_model(data, mode)
    model = proxy_model.sourceModel()
    if isinstance(data, BsddClass):
        relationship_editor.add_class_columns_to_table(model)
    else:
        relationship_editor.add_property_columns_to_table(model)

    widget.tv_relations.setModel(proxy_model)


def add_field_validators(
    widget: ui.RelationshipWidget,
    relationship_editor: Type[tool.RelationshipEditor],
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


def remove_widget(
    widget: ui.RelationshipWidget,
    relationship_editor: Type[tool.RelationshipEditor],
):
    relationship_editor.unregister_widget(widget)
    relationship_editor.unregister_widget(widget.tv_relations)


def connect_signals(
    relationship_editor: Type[tool.RelationshipEditor],
    project: Type[tool.Project],
):
    relationship_editor.connect_internal_signals()
    project.signaller.data_changed.connect(
        lambda n, v: relationship_editor.update_on_dict_change(n, v, project.get())
    )
    project.signaller.class_added.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    project.signaller.class_removed.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    project.signaller.property_added.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
    project.signaller.property_removed.connect(
        lambda _: relationship_editor.update_all_completers(project.get())
    )
