from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.core import ai_helper as core
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui
    from bsdd_gui.module.class_editor_widget import ui as class_edit_ui

from bsdd_gui.module.property_editor_widget import ui as property_ui
from bsdd_gui.module.class_property_editor_widget import ui as class_property_ui


def connect():
    func = lambda: core.splitter_settings_accepted(tool.AiHelper, tool.Appdata)
    core.fill_settings(func, tool.SettingsWidget)
    core.connect_signals(
        tool.AiHelper,
        tool.AiClassDescription,
        tool.AiPropertyDescription,
        tool.ClassEditorWidget,
        tool.PropertyEditorWidget,
        tool.ClassPropertyEditorWidget,
    )


def settings_created(widget: ui.SettingsWidget):
    core.setup_settings(widget, tool.AiHelper, tool.Appdata)


def retranslate_ui():
    pass


def on_new_project():
    pass


def generate_class_definition(widget: class_edit_ui.ClassEditor):
    core.generate_class_definition(
        widget,
        tool.ClassEditorWidget,
        tool.AiHelper,
        tool.AiClassDescription,
        tool.Project,
        tool.Util,
    )


def generate_property_definition(
    widget: property_ui.PropertyEditor | class_property_ui.ClassPropertyEditor,
):
    core.generate_property_definition(
        widget,
        tool.AiHelper,
        tool.AiPropertyDescription,
        tool.Project,
        tool.MainWindowWidget,
        tool.Util,
    )
