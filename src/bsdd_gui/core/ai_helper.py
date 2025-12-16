from __future__ import annotations
from bsdd_gui.module.ai_helper import ui, constants
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool


def fill_settings(func, settings: Type[tool.SettingsWidget]):
    settings.add_page_to_toolbox(ui.SettingsWidget, "pageGeneral", func)


def setup_settings(
    widget: ui.SettingsWidget,
    ai_helper: Type[tool.AiHelper],
    appdata: Type[tool.Appdata],
):
    ai_helper.set_settings_widget(widget)
    splitter = appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.API_KEY, "")
    language = appdata.get_string_setting(constants.AI_HELPER_SECTION, constants.LANGUAGE, "")
    is_active = appdata.get_bool_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE)
    widget.lineEdit.setText(splitter)
    widget.checkBox.setChecked(is_active)
    widget.cb_language.setCurrentText(language)


def splitter_settings_accepted(ai_helper: Type[tool.AiHelper], appdata: Type[tool.Appdata]):
    widget = ai_helper.get_settings_widget()
    is_seperator_activated = ai_helper.read_checkstate(widget)
    text = ai_helper.read_api_key(widget)
    language = ai_helper.read_language(widget)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.API_KEY, text)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE, is_seperator_activated)
    appdata.set_setting(constants.AI_HELPER_SECTION, constants.LANGUAGE, language)
    
    if not text:
        appdata.set_setting(constants.AI_HELPER_SECTION, constants.IS_ACTIVE, False)
