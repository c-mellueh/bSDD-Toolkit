from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_editor_widget as core
from typing import TYPE_CHECKING
from bsdd_parser import BsddProperty
from PySide6.QtWidgets import QWidget
from . import ui


def connect():
    core.connect_signals(tool.PropertyEditorWidget, tool.ClassPropertyEditorWidget, tool.Project)


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_property_creator(blueprint: dict):
    core.create_property_creator(
        blueprint, tool.PropertyEditorWidget, tool.MainWindowWidget, tool.Project, tool.Util
    )


def create_window(bsdd_property: BsddProperty, parent: QWidget | None):
    core.open_edit_window(
        bsdd_property, parent, tool.PropertyEditorWidget, tool.MainWindowWidget, tool.Project
    )


def widget_created(widget: ui.PropertyEditor):
    core.register_widget(widget, tool.PropertyEditorWidget, tool.AllowedValuesTableView)
    core.add_fields_to_widget(
        widget,
        tool.PropertyEditorWidget,
        tool.AllowedValuesTableView,
        tool.RelationshipEditorWidget,
    )
    core.add_validator_functions_to_widget(
        widget, tool.PropertyEditorWidget, tool.Util, tool.Project
    )


def widget_closed(widget: ui.PropertyEditor):
    core.unregister_widget(widget, tool.PropertyEditorWidget, tool.AllowedValuesTableView)
