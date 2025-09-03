from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import dictionary_editor_widget as core
from bsdd_parser import BsddDictionary
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_to_main_window(tool.DictionaryEditorWidget, tool.MainWindowWidget, tool.Project)
    core.connect_signals(tool.DictionaryEditorWidget, tool.Project)


def retranslate_ui():
    core.retranslate_ui(tool.DictionaryEditorWidget, tool.MainWindowWidget, tool.Util)


def on_new_project():
    pass


def create_widget(data: BsddDictionary, parent: QWidget | None):
    core.create_widget(data, parent, tool.DictionaryEditorWidget, tool.MainWindowWidget, tool.Util)


def widget_created(widget: ui.DictionaryEditor):
    core.register_widget(widget, tool.DictionaryEditorWidget)
    core.register_fields(widget, tool.DictionaryEditorWidget)
    core.register_validators(widget, tool.DictionaryEditorWidget, tool.Util)
    core.connect_widget(widget, tool.DictionaryEditorWidget)


def widget_close_requested(widget: ui.DictionaryEditor, event: QCloseEvent):
    core.remove_widget(widget, event, tool.DictionaryEditorWidget, tool.Popups)
