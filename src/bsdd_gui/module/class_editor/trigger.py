from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import class_editor as core
from bsdd_parser import BsddClass
from typing import TYPE_CHECKING


def connect():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def open_class_editor(bsdd_class: BsddClass):
    core.open_class_editor(bsdd_class, tool.ClassEditor)
