from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_gui.module.ai_helper import ui
import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.ai_helper.prop import AiHelperProperties


class AiHelper:
    @classmethod
    def get_properties(cls) -> AiHelperProperties:
        return bsdd_gui.AiHelperProperties

    @classmethod
    def set_settings_widget(cls, widget: ui.SettingsWidget):
        cls.get_properties().settings_widget = widget

    @classmethod
    def get_settings_widget(cls) -> ui.SettingsWidget | None:
        return cls.get_properties().settings_widget
    
    @classmethod
    def get_checkstate(cls,widget: ui.SettingsWidget) -> bool:
        return widget.checkBox.isChecked()
    
    @classmethod
    def read_api_key(cls, widget: ui.SettingsWidget) -> str:
        return widget.lineEdit.text()
    