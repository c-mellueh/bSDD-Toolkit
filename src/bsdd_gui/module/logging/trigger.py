from bsdd_gui import tool
from bsdd_gui.core import logging as core
from . import ui


def connect():
    core.create_logger(tool.Logging, tool.Util, tool.MainWindow)
    tool.Settings.add_page_to_toolbox(
        ui.SettingsWidget,
        "pageLogging",
        lambda: core.settings_accepted(tool.Logging, tool.Util),
    )


def on_new_project():
    pass


def retranslate_ui():
    pass


def settings_widget_created(widget: ui.SettingsWidget):
    core.settings_widget_created(widget, tool.Logging, tool.Util)
    pass
