from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import ids_exporter as core
from typing import TYPE_CHECKING


def connect():
    core.connect_to_main_window(tool.IdsExporter,tool.MainWindowWidget,tool.Project)

def retranslate_ui():
    core.retranslate_ui(tool.GraphViewWidget, tool.MainWindowWidget)

def on_new_project():
    pass
