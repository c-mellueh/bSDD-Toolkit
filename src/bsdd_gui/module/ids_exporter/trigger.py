from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import ids_exporter as core
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import IdsWidget

def connect():
    core.connect_to_main_window(tool.IdsExporter,tool.MainWindowWidget,tool.Project)
    core.connect_signals(tool.IdsExporter)
def retranslate_ui():
    core.retranslate_ui(tool.GraphViewWidget, tool.MainWindowWidget)

def on_new_project():
    pass


def create_widget(data: object, parent: IdsWidget):
    core.create_widget(data, parent, tool.IdsExporter)


def create_dialog(data: object, parent: IdsWidget):
    core.create_dialog(data, parent, tool.IdsExporter)


def widget_created(widget: IdsWidget):
    core.register_widget(widget, tool.IdsExporter)
    core.register_fields(widget, tool.IdsExporter)
    core.register_validators(widget, tool.IdsExporter, tool.Util)
    core.connect_widget(widget, tool.IdsExporter)