import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.LoinProperties = prop.LoinProperties()
    bsdd_gui.PPClassViewProperties = prop.PPClassViewProperties()
    bsdd_gui.PPPropertyViewProperties = prop.PPPropertyViewProperties()

def retranslate_ui():
    trigger.retranslate_ui()

def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()

