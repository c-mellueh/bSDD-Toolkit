from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import graph_view_widget as core
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING


def connect():
    core.connect_signals(tool.GraphViewWidget)
    core.connect_to_main_window(tool.GraphViewWidget, tool.MainWindowWidget)


def retranslate_ui():
    core.retranslate_ui(tool.GraphViewWidget, tool.MainWindowWidget)


def on_new_project():
    pass


def widget_created(widget):
    core.register_widget(widget, tool.GraphViewWidget)
    core.connect_widget(widget, tool.GraphViewWidget)


def create_widget(parent: QWidget | None = None):
    core.create_widget(parent, tool.GraphViewWidget, tool.MainWindowWidget)
