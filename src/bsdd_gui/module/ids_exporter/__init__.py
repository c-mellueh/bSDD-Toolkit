import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.IdsExporterProperties = prop.IdsExporterProperties()
    bsdd_gui.IdsClassViewProperties = prop.IdsClassViewProperties()
    bsdd_gui.IdsPropertyViewProperties = prop.IdsPropertyViewProperties()


def retranslate_ui():
    trigger.retranslate_ui()


def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()
