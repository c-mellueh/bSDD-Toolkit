from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Type

from PySide6.QtWidgets import QCheckBox, QFormLayout

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.plugins import ui


def settings_accepted(plugins: Type[tool.Plugins]):
    layout: QFormLayout = plugins.get_settings_widget().layout()
    for index, plugin_name in enumerate(plugins.get_available_plugins()):
        cb: QCheckBox = layout.itemAt(index, QFormLayout.ItemRole.FieldRole).widget()
        new_checkstate = cb.isChecked()
        old_checkstate = plugins.is_plugin_active(plugin_name)
        friendly_name = plugins.get_friendly_name(plugin_name)
        if new_checkstate == old_checkstate:
            continue
        if new_checkstate:
            plugins.activate_plugin(plugin_name)
        else:
            plugins.deactivate_plugin(plugin_name)


def settings_widget_created(widget: ui.SettingsWidget, plugins: Type[tool.Plugins]):
    layout: QFormLayout = widget.layout()
    plugins.set_settings_widget(widget)
    for plugin_name in plugins.get_available_plugins():
        label, checkbox = plugins.create_settings_entry(plugin_name)
        layout.addRow(label, checkbox)
