from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from . import ui
from bsdd_parser import BsddClassProperty
from bsdd_gui.presets.prop_presets import WidgetProperties


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


class ClassPropertyEditorWidgetProperties(WidgetProperties):

    def __init__(self):
        super().__init__()
        self.plugin_widget_list: list[PluginProperty] = list()
        self.dialog: ui.ClassPropertyCreator = None
        self.splitter_settings: ui.SplitterSettings = None
