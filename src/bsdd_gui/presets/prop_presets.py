from PySide6.QtWidgets import QAbstractItemView, QWidget
from PySide6.QtCore import QAbstractItemModel
from PySide6.QtGui import QAction
from typing import TypedDict, Callable, TypeAlias
from bsdd_gui.presets.ui_presets import ItemViewType
from .models_presets import ItemModel
from dataclasses import dataclass


class ContextMenuDict(TypedDict):
    label_func: Callable[[], str]  # returns label text for the action
    action_func: Callable[..., None]  # function executed when triggered
    allow_single: bool  # available for single selection
    allow_multi: bool  # available for multi-selection
    require_selection: bool  # only enabled if something is selected
    action: QAction  # actual QAction object


class ActionsProperties:
    def __init__(self):
        super().__init__()
        self.actions = dict()


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


class WidgetProperties:
    def __init__(self):
        super().__init__()
        self.widgets = set()
        self.plugin_widget_list: list[PluginProperty] = list()


class FieldProperties(WidgetProperties):
    def __init__(self):
        super().__init__()
        self.field_getter: dict[ItemViewType, dict[ItemViewType, callable]] = (
            dict()
        )  # getter function for widgets of Window
        self.field_setter: dict[ItemViewType, dict[ItemViewType, callable]] = (
            dict()
        )  # getter function for widgets of Window
        self.validator_functions: dict[
            ItemViewType, dict[ItemViewType, list[tuple[callable, callable]]]
        ] = dict()


class DialogProperties(FieldProperties):
    def __init__(self):
        super().__init__()
        self.dialog = None


class ViewProperties:
    def __init__(self):
        super().__init__()
        self.context_menu_list: dict[QAbstractItemView, list[ContextMenuDict]] = dict()
        self.columns: dict[QAbstractItemModel, list[tuple[str, callable]]] = dict()
        self.models: set[ItemModel] = set()
        self.views: set[ItemViewType] = set()
