from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import dictionary_editor as core
from PySide6.QtGui import QCloseEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.create_main_menu_actions(tool.DictionaryEditor, tool.MainWindow)
    core.connect_signals(tool.DictionaryEditor, tool.Project, tool.MainWindow, tool.Util)


def retranslate_ui():
    core.retranslate_ui(tool.DictionaryEditor, tool.MainWindow, tool.Util)


def on_new_project():
    pass


def widget_created(widget: ui.DictionaryEditor):
    core.connect_widget(widget, tool.DictionaryEditor)
    pass


def widget_close_requested(widget: ui.DictionaryEditor, event: QCloseEvent):
    core.remove_widget(widget, event, tool.DictionaryEditor, tool.Popups)
