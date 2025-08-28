from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import property_editor as core
from typing import TYPE_CHECKING
from bsdd_parser import BsddProperty
from PySide6.QtWidgets import QWidget


def connect():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def create_window(bsdd_property: BsddProperty, parent: QWidget):
    core.open_edit_window(bsdd_property, parent, tool.PropertyEditor, tool.MainWindow, tool.Project)
