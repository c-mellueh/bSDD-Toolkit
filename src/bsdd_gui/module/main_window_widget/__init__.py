import bsdd_gui
from . import prop, trigger, ui


def register():
    bsdd_gui.MainWindowWidgetProperties = prop.MainWindowWidgetProperties()


def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()


def retranslate_ui():
    trigger.retranslate_ui()
