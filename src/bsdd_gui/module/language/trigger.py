from __future__ import annotations

from bsdd_gui import tool
from bsdd_gui.core import language as core
from bsdd_gui.module.language import ui


def connect():
    tool.Settings.add_page_to_toolbox(
        ui.SettingsWidget, "pageGeneral", lambda: core.settings_accepted(tool.Language)
    )


def settings_widget_created(widget: ui.SettingsWidget):
    core.settings_widget_created(widget, tool.Language)


def on_new_project():
    pass


def retranslate_ui():
    core.retranslate_ui(tool.Language)


def set_language(language_code: str | None):
    core.set_language(language_code, tool.Language, tool.Appdata, tool.MainWindow, tool.Plugins)
