from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.dictionary_editor import ui


def connect_widget(widget: ui.DictionaryEditor, dictionary_editor: Type[tool.DictionaryEditor]):
    dictionary_editor.register_widget(widget)
    dictionary_editor.fill_dictionary_widget(widget)
