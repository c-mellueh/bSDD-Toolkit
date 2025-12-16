from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import ai_helper as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui
    from bsdd_gui.module.class_editor_widget import ui as class_edit_ui


def connect():
    func = lambda: core.splitter_settings_accepted(tool.AiHelper, tool.Appdata)
    core.fill_settings(func, tool.SettingsWidget)
    core.connect_signals(tool.AiHelper,tool.AiClassDescription, tool.ClassEditorWidget)


def settings_created(widget: ui.SettingsWidget):
    core.setup_settings(widget, tool.AiHelper, tool.Appdata)


def retranslate_ui():
    pass


def on_new_project():
    pass


def generate_class_definition(widget: class_edit_ui.ClassEditor):
    core.generate_class_definition(
        widget, tool.ClassEditorWidget,tool.AiHelper, tool.AiClassDescription, tool.Project, tool.Util
    )
