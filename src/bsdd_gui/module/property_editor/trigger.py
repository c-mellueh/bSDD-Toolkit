from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_editor as core
from typing import TYPE_CHECKING
from bsdd_parser import BsddProperty
from PySide6.QtWidgets import QWidget
from . import ui


def connect():
    core.connect_signals(tool.PropertyEditor, tool.ClassPropertyEditor, tool.Project)


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_property_creator(blueprint: dict):
    core.create_property_creator(
        blueprint, tool.PropertyEditor, tool.MainWindow, tool.Project, tool.Util
    )


def create_window(bsdd_property: BsddProperty, parent: QWidget | None):
    core.open_edit_window(bsdd_property, parent, tool.PropertyEditor, tool.MainWindow, tool.Project)


def widget_created(widget: ui.PropertyEditor):
    core.register_widget(widget, tool.PropertyEditor)
    core.add_fields_to_widget(widget, tool.PropertyEditor, tool.AllowedValuesTable)
    core.add_validator_functions_to_widget(widget, tool.PropertyEditor, tool.Util, tool.Project)


def widget_closed(widget: ui.PropertyEditor):
    core.unregister_widget(widget, tool.PropertyEditor)
