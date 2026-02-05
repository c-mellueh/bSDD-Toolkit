import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.GroupOfPropertiesProperties = prop.GroupOfPropertiesProperties()
    bsdd_gui.GopClassViewProperties = prop.GopClassViewProperties()
    bsdd_gui.GopPropertyViewProperties = prop.GopPropertyViewProperties()


def retranslate_ui():
    trigger.retranslate_ui()


def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()
