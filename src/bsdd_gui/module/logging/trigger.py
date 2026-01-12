from bsdd_gui import tool
from bsdd_gui.core import logging as core
from . import ui


def connect():
    func = lambda: core.settings_accepted(tool.Logging, tool.Util)
    core.add_settings_page(func, tool.SettingsWidget)
    core.create_logger(tool.Logging, tool.Util, tool.MainWindowWidget)


def on_new_project():
    pass


def retranslate_ui():
    pass


def settings_widget_created(widget: ui.SettingsWidget):
    core.settings_widget_created(widget, tool.Logging, tool.Util)
    pass
