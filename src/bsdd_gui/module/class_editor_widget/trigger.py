from __future__ import annotations
from bsdd_gui import tool
from bsdd_gui.core import class_editor_widget as core
from bsdd_json import BsddClass
from typing import TYPE_CHECKING, Type
import logging

if TYPE_CHECKING:
    from . import ui
    from .constants import CLASS_TYPES
### Basic Triggers


def connect():
    core.connect_to_main_window(tool.ClassEditorWidget, tool.MainWindowWidget)
    core.connect_signals(tool.ClassEditorWidget, tool.Project)


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_widget(*args, **kwargs):
    logging.error("Function not defined!")


def create_dialog(allowed_class_types, bsdd_class: BsddClass):
    core.edit_class(allowed_class_types, bsdd_class, tool.ClassEditorWidget, tool.MainWindowWidget)


def widget_created(widget: ui.ClassEditor):
    core.register_widget(widget, tool.ClassEditorWidget)
    core.register_fields(widget, tool.ClassEditorWidget)
    core.register_validators(widget, tool.ClassEditorWidget, tool.Project, tool.Util)
    core.connect_widget(widget, tool.ClassEditorWidget, tool.RelationshipEditorWidget)


### Module Specific Triggers


def create_new_class(class_type: CLASS_TYPES, parent_class: BsddClass | None):
    core.create_new_class(class_type, parent_class, tool.ClassEditorWidget, tool.MainWindowWidget)


def group_classes(
    class_tree_tool: Type[tool.ClassTreeView | tool.GopClassView], bsdd_classes: list[BsddClass]
):
    core.group_classes(
        bsdd_classes, tool.ClassEditorWidget, tool.MainWindowWidget, tool.Project, class_tree_tool
    )
