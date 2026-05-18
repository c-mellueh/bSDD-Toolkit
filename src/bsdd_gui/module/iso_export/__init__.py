import bsdd_gui
from . import prop, trigger


def register():
    bsdd_gui.IsoExportProperties = prop.IsoExportProperties()


def retranslate_ui():
    trigger.retranslate_ui()


def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()
