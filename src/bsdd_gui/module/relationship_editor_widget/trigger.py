from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import relationship_editor as core
from typing import TYPE_CHECKING, Literal
from bsdd_parser import BsddClass, BsddProperty
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import QPoint

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(tool.RelationshipEditor, tool.Project, tool.ClassEditor)


def retranslate_ui():
    core.retranslate_ui(tool.RelationshipEditor)


def on_new_project():
    pass


def widget_created(
    widget: ui.RelationshipWidget,
    data: BsddClass | BsddProperty,
    mode: Literal["dialog"] | Literal["live"],
):
    view = widget.tv_relations
    core.register_view(view, tool.RelationshipEditor)
    core.add_columns_to_view(view, data, mode, tool.RelationshipEditor)
    core.add_context_menu_to_view(view, tool.RelationshipEditor)
    core.connect_view(view, tool.RelationshipEditor)

    core.register_widget(widget, tool.RelationshipEditor)
    core.connect_widget(widget, data, mode, tool.RelationshipEditor, tool.Project)
    core.add_field_validators(widget, tool.RelationshipEditor, tool.Util, tool.Project)
    core.retranslate_ui(tool.RelationshipEditor)


def context_menu_requested(view: QTableView, pos: QPoint):
    core.create_context_menu(view, pos, tool.RelationshipEditor)


def widget_closed(widget: ui.RelationshipWidget):
    core.remove_widget(widget, tool.RelationshipEditor)
    core.remove_view(widget.tv_relations, tool.RelationshipEditor)
