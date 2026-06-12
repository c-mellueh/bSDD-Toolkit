from __future__ import annotations

from bsdd_gui import tool
from bsdd_gui.core import theme as core
from bsdd_gui.module.theme import ui


def connect():
    tool.SettingsWidget.add_page_to_toolbox(
        ui.SettingsWidget,
        "pageGeneral",
        lambda: core.settings_accepted(tool.Theme, tool.Appdata, tool.MainWindowWidget),
    )


def settings_widget_created(widget: ui.SettingsWidget):
    core.settings_widget_created(widget, tool.Theme)


def system_scheme_changed(*args):
    core.system_scheme_changed(tool.Theme, tool.MainWindowWidget)


def view_zoom_scrolled(steps: int):
    core.change_view_zoom(steps, tool.Theme, tool.Appdata, tool.MainWindowWidget)


def on_new_project():
    pass


def retranslate_ui():
    core.retranslate_ui(tool.Theme)
