import bsdd_gui
from . import prop, trigger


def register():
    bsdd_gui.GraphViewerEdgeProperties = prop.GraphViewerEdgeProperties()

    
def activate():
    trigger.activate()

    
def deactivate():
    trigger.deactivate()

    
def retranslate_ui():
    trigger.retranslate_ui()

    
def on_new_project():
    trigger.on_new_project()

