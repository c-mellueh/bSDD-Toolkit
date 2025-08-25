from __future__ import annotations
from typing import TYPE_CHECKING
import logging

import bsdd_gui
from bsdd_gui.presets.tool_presets import WidgetHandler

if TYPE_CHECKING:
    from bsdd_gui.module.dictionary_editor.prop import DictionaryEditorProperties


class DictionaryEditor(WidgetHandler):
    @classmethod
    def get_properties(cls) -> DictionaryEditorProperties:
        return bsdd_gui.DictionaryEditorProperties
