from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import relationship_editor_widget as core
from typing import TYPE_CHECKING, Literal
from bsdd_json import BsddClass, BsddProperty
from PySide6.QtWidgets import QTableView
from PySide6.QtCore import QPoint

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(
        tool.RelationshipEditorWidget,
        tool.Project,
        tool.ClassEditorWidget,
        tool.PropertyEditorWidget,
    )
    func = lambda: core.splitter_settings_accepted(tool.RelationshipEditorWidget, tool.Appdata)
    core.add_settings(func, tool.SettingsWidget)


def retranslate_ui():
    core.retranslate_ui(tool.RelationshipEditorWidget)


def on_new_project():
    pass


def create_widget(*args, **kwargs):
    pass


def widget_created(
    widget: ui.RelationshipWidget,
    data: BsddClass | BsddProperty,
    mode: Literal["dialog"] | Literal["live"],
):
    view = widget.tv_relations
    core.register_view(view, tool.RelationshipEditorWidget)
    core.add_columns_to_view(view, data, mode, tool.RelationshipEditorWidget)
    core.add_context_menu_to_view(view, tool.RelationshipEditorWidget)
    core.connect_view(view, tool.RelationshipEditorWidget)

    core.register_widget(widget, data, tool.RelationshipEditorWidget)
    core.register_fields(widget, tool.RelationshipEditorWidget)
    core.register_validators(widget, tool.RelationshipEditorWidget, tool.Util, tool.Project)
    core.connect_widget(widget, data, mode, tool.RelationshipEditorWidget, tool.Project)

    core.retranslate_ui(tool.RelationshipEditorWidget)


def context_menu_requested(view: QTableView, pos: QPoint):
    core.create_context_menu(view, pos, tool.RelationshipEditorWidget)


def widget_closed(widget: ui.RelationshipWidget):
    core.remove_widget(widget, tool.RelationshipEditorWidget)
    core.remove_view(widget.tv_relations, tool.RelationshipEditorWidget)


def settings_created(widget: ui.SettingsWidget):
    core.load_splitter_settings(widget, tool.RelationshipEditorWidget, tool.Appdata)
