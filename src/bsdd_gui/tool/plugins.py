from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Any, TYPE_CHECKING

from PySide6.QtWidgets import QCheckBox, QLabel

import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.module.plugins import constants

if TYPE_CHECKING:
    from bsdd_gui.module.plugins.prop import PluginsProperties
    from bsdd_gui.module.plugins import ui


class Plugins:

    @classmethod
    def get_properties(cls) -> PluginsProperties:
        return bsdd_gui.PluginsProperties

    @classmethod
    def get_settings_widget(cls) -> ui.SettingsWidget:
        return cls.get_properties().settings_widget

    @classmethod
    def set_settings_widget(cls, widget: ui.SettingsWidget):
        cls.get_properties().settings_widget = widget

    @classmethod
    def get_available_plugins(cls) -> list[str]:
        module = importlib.import_module("bsdd_gui.plugins")
        modules = sorted(m.name for m in pkgutil.iter_modules(module.__path__) if m.ispkg)
        return modules

    @classmethod
    def get_submodules(cls, plugin_name: str) -> list[tuple[str, Any]]:
        module_text = f"bsdd_gui.plugins.{plugin_name}.module"
        logging.info(f"Import Plugin {plugin_name} -> {module_text}")

        submodule_names = [
            m.name
            for m in pkgutil.iter_modules(importlib.import_module(module_text).__path__)
            if m.ispkg
        ]
        logging.info(f"Submodules: {submodule_names}")
        submodules = [importlib.import_module(f"{module_text}.{n}") for n in submodule_names]
        return list(zip(submodule_names, submodules))

    @classmethod
    def is_plugin_active(cls, plugin_name: str) -> bool:
        return tool.Appdata.get_bool_setting(constants.PLUGINS, plugin_name)

    @classmethod
    def set_plugin_active(cls, plugin_name: str, state: bool) -> None:
        tool.Appdata.set_setting(constants.PLUGINS, plugin_name, state)

    @classmethod
    def get_friendly_name(cls, name: str):
        module = importlib.import_module(f"bsdd_gui.plugins.{name}")
        if not "friendly_name" in dir(module):
            return name
        return getattr(module, "friendly_name")

    @classmethod
    def get_description(cls, name: str):
        module = importlib.import_module(f"bsdd_gui.plugins.{name}")
        if not "description" in dir(module):
            return ""
        return getattr(module, "description")

    @classmethod
    def create_settings_entry(cls, plugin_name: str) -> tuple[QLabel, QCheckBox]:
        cb = QCheckBox()
        cb.setChecked(cls.is_plugin_active(plugin_name))

        friendly_name = cls.get_friendly_name(plugin_name)
        label = QLabel(friendly_name)
        label.setToolTip(cls.get_description(plugin_name))
        return label, cb

    @classmethod
    def activate_plugin(cls, plugin_name: str):
        module = importlib.import_module(f"bsdd_gui.plugins.{plugin_name}")
        if not "activate" in dir(module):
            return None
        module.activate()
        cls.set_plugin_active(plugin_name, True)

    @classmethod
    def deactivate_plugin(cls, plugin_name: str):
        module = importlib.import_module(f"bsdd_gui.plugins.{plugin_name}")
        if not "deactivate" in dir(module):
            return None
        module.deactivate()
        cls.set_plugin_active(plugin_name, False)

    @classmethod
    def on_new_project(cls, plugin_name: str):
        if not cls.is_plugin_active(plugin_name):
            return
        module = importlib.import_module(f"bsdd_gui.plugins.{plugin_name}")
        if not "on_new_project" in dir(module):
            return None
        module.on_new_project()
