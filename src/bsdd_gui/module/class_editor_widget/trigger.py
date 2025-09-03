from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_editor_widget as core
from bsdd_parser import BsddClass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.ClassEditorWidget, tool.MainWindowWidget, tool.Project)
    core.connect_signals(tool.ClassEditorWidget, tool.Project)


def retranslate_ui():
    pass


def on_new_project():
    pass


def open_widget(bsdd_class: BsddClass):
    core.open_dialog(bsdd_class, tool.ClassEditorWidget, tool.MainWindowWidget)


def widget_created(class_editor: ui.ClassEditor):
    core.register_widget(
        class_editor, tool.ClassEditorWidget, tool.Project, tool.Util, tool.RelationshipEditorWidget
    )


def copy_class(bsdd_class: BsddClass):
    core.copy_class(bsdd_class, tool.ClassEditorWidget, tool.MainWindowWidget)


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
