from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import settings as core
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_signals(gv_tool.Settings, gv_tool.Window, gv_tool.SceneView)


def deactivate():
    core.disconnect_signals(gv_tool.Settings)


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_widget():
    core.create_widget(gv_tool.Settings)


def widget_created(widget: ui.SettingsWidget):
    core.register_widget(widget, gv_tool.Settings, gv_tool.SceneView)
    core.connect_widget(widget, gv_tool.Settings)
