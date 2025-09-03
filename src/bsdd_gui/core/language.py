from __future__ import annotations

from typing import TYPE_CHECKING, Type

from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.language import ui
import bsdd_gui
import importlib

SECTION = "langugage"
PATH = "current_language"


def settings_widget_created(widget: ui.SettingsWidget, language: Type[tool.Language]):
    language.set_widget(widget)
    retranslate_ui(language)


def settings_accepted(language: Type[tool.Language]):
    from bsdd_gui.module.language import trigger

    widget = language.get_widget()
    cb = widget.ui.comboBox
    code = cb.currentData()
    trigger.set_language(code)


def set_language(
    code: str | None,
    language: Type[tool.Language],
    appdata: Type[tool.Appdata],
    main_window: Type[tool.MainWindowWidget],
    plugings: Type[tool.Plugins],
):
    """
    Sets UI Language
    if code is None checks last unsed language or System-Language
    """
    if code is None:
        system_lang = language.get_system_language()
        code = appdata.get_string_setting(SECTION, PATH, system_lang)

    language.set_language(code)
    appdata.set_setting(SECTION, PATH, code)

    app = main_window.get_app()
    language.load_main_translations(app, code)
    language.retranslate_main_ui()

    active_plugins = [n for n in plugings.get_available_plugins() if plugings.is_plugin_active(n)]
    language.load_plugin_translations(active_plugins, app, code)
    language.retranslate_plugins(active_plugins)


def retranslate_ui(language: Type[tool.Language]):
    widget = language.get_widget()
    if not widget:
        return
    widget.ui.retranslateUi(widget)
    combobox = widget.ui.comboBox
    combobox.clear()
    combobox.addItem(QCoreApplication.translate("Settings", "German"), "de")
    combobox.addItem(QCoreApplication.translate("Settings", "English"), "en")
    current_lang = language.get_language()
    for item in range(combobox.count()):
        if combobox.itemData(item) == current_lang:
            combobox.setCurrentIndex(item)
