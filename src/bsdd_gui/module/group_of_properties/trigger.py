from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import group_of_properties as core
from typing import TYPE_CHECKING



def connect():
    core.connect_to_main_window(tool.GroupOfProperties, tool.MainWindowWidget, tool.Project)
    core.connect_signals(tool.GroupOfProperties)


def retranslate_ui():
    core.retranslate_ui(tool.GroupOfProperties, tool.MainWindowWidget)


def on_new_project():
    pass




def create_widget(data: object, parent):
    core.create_widget(data, parent, tool.GroupOfProperties)

def widget_created(widget):
    core.register_widget(widget, tool.GroupOfProperties)
    core.connect_widget(widget, tool.GroupOfProperties)
