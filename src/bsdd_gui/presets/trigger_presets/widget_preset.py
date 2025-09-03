# This File can be copied and modified to fit your Module
# It contains the minimum amount of triggers needed to make an ItemView Work

from __future__ import annotations
import bsdd_gui
from typing import TYPE_CHECKING
from bsdd_gui.presets.ui_presets import ItemViewType
from PySide6.QtCore import QPoint

from bsdd_gui.presets.core_presets import widget_preset as core  # <- modify to fit your need
from bsdd_gui.presets import tool_presets as tool  # <- modify to fit your need
from bsdd_gui.presets.ui_presets import FieldWidget

if TYPE_CHECKING:
    from . import ui

### Basic Triggers


def connect():
    core.connect_signals(tool.ItemViewTool)


def retranslate_ui():
    core.retranslate_ui(tool.ItemViewTool)


def on_new_project():
    pass


def open_widget(data: object, parent: FieldWidget):
    core.open_widget(data, parent, tool.WidgetTool)


def open_dialog(data: object, parent: FieldWidget):
    core.open_dialog(data, parent, tool.DialogTool)


def widget_created(widget: FieldWidget):
    core.register_widget(widget, tool.ItemViewTool)
    core.register_fields(widget, tool.ItemViewTool)
    core.register_validators(widget, tool.ItemViewTool, tool.Util)
    core.connect_widget(widget, tool.ItemViewTool)


### Module Specific Triggers
