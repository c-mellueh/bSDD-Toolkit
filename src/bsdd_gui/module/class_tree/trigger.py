from __future__ import annotations
from typing import TYPE_CHECKING
from bsdd_gui import tool
from bsdd_gui.core import class_tree as core
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QDropEvent

TOOGLE_CONSOLE_ACTION = "toggle_console"
if TYPE_CHECKING:
    from . import ui

def connect():
    pass

def on_new_project():
    pass

def retranslate_ui():
    pass

def close_event(event):
    pass

def class_view_created(class_view:ui.ClassView):
    core.connect_class_view(class_view,tool.ClassTree,tool.Project)