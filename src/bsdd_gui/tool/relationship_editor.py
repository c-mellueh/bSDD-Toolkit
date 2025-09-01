from __future__ import annotations
from typing import TYPE_CHECKING, Literal
import logging


import bsdd_gui
from bsdd_parser import BsddProperty, BsddClass

if TYPE_CHECKING:
    from bsdd_gui.module.relationship_editor.prop import RelationshipEditorProperties
    from bsdd_gui.module.relationship_editor import ui, trigger


class RelationshipEditor:
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
