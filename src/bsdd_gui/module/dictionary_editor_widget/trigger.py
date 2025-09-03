from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import dictionary_editor_widget as core
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.create_main_menu_actions(tool.DictionaryEditor, tool.MainWindow, tool.Project)
    core.connect_signals(tool.DictionaryEditor, tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.DictionaryEditor, tool.MainWindow, tool.Util)


def on_new_project():
    pass


def widget_close_requested(widget: ui.DictionaryEditor, event: QCloseEvent):
    core.remove_widget(widget, event, tool.DictionaryEditor, tool.Popups)


def widget_closed(widget: ui.DictionaryEditor):
    core.unregister_widget(widget, tool.DictionaryEditor)


def create_widget(widget: ui.DictionaryEditor, parent: QWidget | None):
    core.open_widget(widget, parent, tool.DictionaryEditor, tool.MainWindow, tool.Util)


def widget_created(widget: ui.DictionaryEditor):
    core.register_widget(widget, tool.DictionaryEditor)
    core.add_fields_to_widget(widget, tool.DictionaryEditor)
    core.add_validator_functions_to_widget(widget, tool.DictionaryEditor, tool.Util)
