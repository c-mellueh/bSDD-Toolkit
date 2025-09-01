from __future__ import annotations

from typing import TYPE_CHECKING, Type, Literal
from bsdd_parser import BsddProperty, BsddClass

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.relationship_editor import ui


def connect_widget(
    widget: ui.RelationshipWidget,
    data: BsddClass | BsddProperty,
    mode: Literal["dialog"] | Literal["live"],
    relationship_editor: Type[tool.RelationshipEditor],
):

    relationship_editor.register_widget(widget)
    relationship_editor.register_widget(widget.tv_relations)
    widget.data = data
    widget.mode = mode
    relationship_editor.connect_widget_signals(widget)


def add_field_validators(
    widget: ui.RelationshipWidget,
    relationship_editor: Type[tool.RelationshipEditor],
    util: Type[tool.Util],
    project: Type[tool.Project],
):
    relationship_editor.add_validator(
        widget,
        widget.le_related_class,
        lambda v, w,: relationship_editor.is_related_class_valid(v, w, project.get()),
        lambda w, v: util.set_invalid(w, not v),
    )


def remove_widget(
    widget: ui.RelationshipWidget,
    relationship_editor: Type[tool.RelationshipEditor],
):
    relationship_editor.unregister_widget(widget)
    relationship_editor.unregister_widget(widget.tv_relations)


def connect_signals(
    relationship_editor: Type[tool.RelationshipEditor],
):
    relationship_editor.connect_internal_signals()
