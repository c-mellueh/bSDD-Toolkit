from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import relationship_editor as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    pass


def retranslate_ui():
    pass


def on_new_project():
    pass


def widget_created(widget: ui.RelationshipWidget):
    core.connect_widget(widget, tool.RelationshipEditor)
