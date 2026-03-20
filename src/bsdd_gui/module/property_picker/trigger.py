from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_picker as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.PropertyPicker)


def retranslate_ui():
    core.retranslate_ui(tool.PropertyPicker)

def on_new_project():
    pass

def create_widget(data: object, parent: ui.Widget):
    core.create_widget(data, parent, tool.PropertyPicker)


#def create_dialog(data: object, parent: ui.Widget):
#    core.create_dialog(data, parent, tool.PropertyPicker)


def widget_created(widget: ui.Widget):
    core.register_widget(widget, tool.PropertyPicker)
    core.register_fields(widget, tool.PropertyPicker)
    core.register_validators(widget, tool.PropertyPicker, tool.Util)
    core.connect_widget(widget, tool.PropertyPicker)

