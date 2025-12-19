from __future__ import annotations

import importlib
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

import bsdd_gui

if TYPE_CHECKING:
    from bsdd_gui.module.language.prop import LanguageProperties
    from bsdd_gui.module.language import ui

from bsdd_gui.resources.translation import load_language


class Language:
    @classmethod
    def get_properties(cls) -> LanguageProperties:
        return bsdd_gui.LanguageProperties

    @classmethod
    def set_widget(cls, widget: ui.SettingsWidget):
        cls.get_properties().widget = widget

    @classmethod
    def get_widget(cls) -> ui.SettingsWidget:
        return cls.get_properties().widget

    @classmethod
    def set_language(cls, code: str):
        cls.get_properties().current_language = code

    @classmethod
    def get_language(cls) -> str:
        return cls.get_properties().current_language

    @classmethod
    def get_system_language(cls) -> str:
        return QLocale.system().countryToCode(QLocale.system().country()).lower()

    @classmethod
    def load_main_translations(cls, app: QApplication, lang_code: str):
        load_language(app, lang_code)

    @classmethod
    def load_plugin_translations(cls, plugin_names: list[str], app: QApplication, lang_code: str):
        for plugin_name in plugin_names:
            module_text = f"bsdd_gui.plugins.{plugin_name}"
            try:
                text = f"{module_text}.resources.translation"
                module = importlib.import_module(text)
                module.load_language(app, lang_code)
            except ModuleNotFoundError:
                #TODO: Add Plugin Translation for Graph Viewer
                logging.info(f"Plugin '{plugin_name}' has no translation")

    @classmethod
    def retranslate_main_ui(cls):
        bsdd_gui.retranslate_ui()

    @classmethod
    def retranslate_plugins(cls, plugin_names: list[str]):
        for plugin_names in plugin_names:
            module = importlib.import_module(f"bsdd_gui.plugins.{plugin_names}")
            module.retranslate_ui()
