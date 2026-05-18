import bsdd_gui
from . import prop, trigger, ui as ui


def register():
    bsdd_gui.GraphViewerWindowProperties = prop.GraphViewerWindowProperties()


def activate():
    trigger.activate()


def deactivate():
    trigger.deactivate()


def retranslate_ui():
    trigger.retranslate_ui()


def on_new_project():
    trigger.on_new_project()
