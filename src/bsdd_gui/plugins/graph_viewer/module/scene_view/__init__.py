import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.GraphViewerSceneViewProperties = prop.GraphViewerSceneViewProperties()


def activate():
    trigger.activate()


def deactivate():
    trigger.deactivate()


def retranslate_ui():
    trigger.retranslate_ui()


def on_new_project():
    trigger.on_new_project()
