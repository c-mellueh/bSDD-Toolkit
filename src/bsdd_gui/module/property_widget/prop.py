from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass
from PySide6.QtWidgets import QWidget
from . import ui
from bsdd_parser import BsddClassProperty


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


class PropertyWidgetProperties:
    plugin_widget_list: list[PluginProperty] = list()
    windows: dict[BsddClassProperty, ui.PropertyWindow] = dict()
    context_menu_builders = list()
    splitter_settings: ui.SplitterSettings = None
