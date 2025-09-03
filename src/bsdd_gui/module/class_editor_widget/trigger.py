from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_editor_widget as core
from bsdd_parser import BsddClass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.ClassEditor, tool.MainWindow, tool.Project)
    core.connect_signals(tool.ClassEditor, tool.Project)


def retranslate_ui():
    pass


def on_new_project():
    pass


def open_class_editor(bsdd_class: BsddClass):
    core.open_class_editor(bsdd_class, tool.ClassEditor, tool.MainWindow)


def copy_class(bsdd_class: BsddClass):
    core.copy_class(bsdd_class, tool.ClassEditor, tool.MainWindow)


def create_new_class(parent_class: BsddClass | None):
    core.create_new_class(parent_class, tool.ClassEditor, tool.MainWindow)


def group_classes(bsdd_classes: list[BsddClass]):
    core.group_classes(
        bsdd_classes, tool.ClassEditor, tool.MainWindow, tool.Project, tool.ClassTree
    )


def class_editor_created(class_editor: ui.ClassEditor):
    core.register_widget(
        class_editor, tool.ClassEditor, tool.Project, tool.Util, tool.RelationshipEditor
    )
