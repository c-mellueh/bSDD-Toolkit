import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.RelationshipEditorProperties = prop.RelationshipEditorProperties()


def retranslate_ui():
    trigger.retranslate_ui()


def load_ui_triggers():
    trigger.connect()


def on_new_project():
    trigger.on_new_project()
