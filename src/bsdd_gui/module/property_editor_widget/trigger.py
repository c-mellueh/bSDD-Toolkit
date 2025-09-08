from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_editor_widget as core
from typing import TYPE_CHECKING
from bsdd_json import BsddProperty
from PySide6.QtWidgets import QWidget
from . import ui


def connect():
    core.connect_signals(tool.PropertyEditorWidget, tool.ClassPropertyEditorWidget, tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.PropertyEditorWidget)


def on_new_project():
    pass


def create_widget(bsdd_property: BsddProperty, parent: QWidget | None):
    core.create_widget(bsdd_property, parent, tool.PropertyEditorWidget, tool.MainWindowWidget)


def create_dialog(blueprint: dict, parent: QWidget):
    core.create_dialog(
        blueprint, parent, tool.PropertyEditorWidget, tool.MainWindowWidget, tool.Project, tool.Util
    )


def widget_created(widget: ui.PropertyEditor):
    core.register_widget(widget, tool.PropertyEditorWidget,tool.AllowedValuesTableView)
    core.register_fields(
        widget,
        tool.PropertyEditorWidget,
        tool.AllowedValuesTableView,
        tool.RelationshipEditorWidget,
    )
    core.register_validators(widget, tool.PropertyEditorWidget, tool.Util, tool.Project)
    core.connect_widget(widget, tool.PropertyEditorWidget, tool.AllowedValuesTableView)
