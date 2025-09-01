from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.relationship_editor.prop import RelationshipEditorProperties


class RelationshipEditor:
    @classmethod
    def get_properties(cls) -> RelationshipEditorProperties:
        return bsdd_gui.RelationshipEditorProperties
