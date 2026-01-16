from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_editor_widget as core
from bsdd_json import BsddClass
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from . import ui

### Basic Triggers


def connect():
    core.connect_to_main_window(tool.ClassEditorWidget, tool.MainWindowWidget)
    core.connect_signals(tool.ClassEditorWidget, tool.Project)


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_widget(*args, **kwargs):
    logging.error(f"Function not defined!")


def create_dialog(bsdd_class: BsddClass):
    core.create_dialog(bsdd_class, tool.ClassEditorWidget, tool.MainWindowWidget)


def widget_created(widget: ui.ClassEditor):
    core.register_widget(widget, tool.ClassEditorWidget)
    core.register_fields(widget, tool.ClassEditorWidget)
    core.register_validators(widget, tool.ClassEditorWidget, tool.Project, tool.Util)
    core.connect_widget(widget, tool.ClassEditorWidget, tool.RelationshipEditorWidget)


### Module Specific Triggers


def create_new_class(parent_class: BsddClass | None):
    core.create_new_class(parent_class, tool.ClassEditorWidget, tool.MainWindowWidget)


def group_classes(bsdd_classes: list[BsddClass]):
    core.group_classes(
        bsdd_classes,
        tool.ClassEditorWidget,
        tool.MainWindowWidget,
        tool.Project,
        tool.ClassTreeView,
    )
