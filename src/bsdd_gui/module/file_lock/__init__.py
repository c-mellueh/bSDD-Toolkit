import bsdd_gui
from . import prop, trigger, ui as ui


def register():
    bsdd_gui.FileLockProperties = prop.FileLockProperties()


def retranslate_ui():
    trigger.retranslate_ui()


def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()
