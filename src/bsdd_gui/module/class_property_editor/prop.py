from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from . import ui
from bsdd_parser import BsddClassProperty
from bsdd_gui.presets.prop_presets import WidgetHandlerProperties


@dataclass
class PluginProperty:
    key: str
    layout_name: str
    widget: QWidget
    index: int
    value_getter: Callable
    value_setter: Callable
    widget_value_setter: Callable
    value_test: Callable


class ClassPropertyEditorProperties(WidgetHandlerProperties):
    plugin_widget_list: list[PluginProperty] = list()
    windows: list[ui.ClassPropertyEditor] = list()
    dialog: ui.ClassPropertyCreator = None
    context_menu_builders = list()
    splitter_settings: ui.SplitterSettings = None
