from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import download as core
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import ui

### Basic Triggers


def connect():
    core.connect_to_main_window(tool.Download,tool.MainWindowWidget,tool.Project)
    core.connect_signals(tool.Download)


def retranslate_ui():
    core.retranslate_ui(tool.Download,tool.MainWindowWidget,tool.Util)


def on_new_project():
    pass


def create_widget( data,parent: ui.DownloadWidget):
    core.create_widget(data,parent, tool.Download)

def widget_created(widget: ui.DownloadWidget):
    core.register_widget(widget, tool.Download)
    core.register_fields(widget, tool.Download,tool.Appdata)
    core.register_validators(widget, tool.Download, tool.Util)
    core.connect_widget(widget, tool.Download)

def start_download(widget:ui.DownloadWidget):
    core.download_dictionary(widget,tool.Download)

### Module Specific Triggers
