import bsdd_gui
from . import ui, prop, trigger


def register():
    bsdd_gui.GraphViewerNodeProperties = prop.GraphViewerNodeProperties()

    
def activate():
    trigger.activate()

    
def deactivate():
    trigger.deactivate()

    
def retranslate_ui():
    trigger.retranslate_ui()

    
def on_new_project():
    trigger.on_new_project()

