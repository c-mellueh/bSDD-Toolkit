from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.property_editor.prop import PropertyEditorProperties


class PropertyEditor:
    @classmethod
    def get_properties(cls) -> PropertyEditorProperties:
        return bsdd_gui.PropertyEditorProperties
