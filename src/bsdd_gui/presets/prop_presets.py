from PySide6.QtWidgets import QAbstractItemView, QWidget
from PySide6.QtCore import QAbstractItemModel
from PySide6.QtGui import QAction
from typing import TypedDict, Callable, TypeAlias
from bsdd_gui.presets.ui_presets import ItemViewType, FieldWidget
from .models_presets import ItemModel
from dataclasses import dataclass


class ContextMenuDict(TypedDict, total=False):
    label_func: Callable[[], str]  # returns label text for the action
    action_func: Callable[..., None]  # function executed when triggered
    allow_single: bool  # available for single selection
    allow_multi: bool  # available for multi-selection
    require_selection: bool  # only enabled if something is selected
    action: QAction | None  # actual QAction object, set when menu is built


class ActionsProperties:
    def __init__(self):
        super().__init__()
        self.actions = dict()


@dataclass
class PluginProperty:
    key: str
    layout_name: str
    widget: Callable[[], QWidget]
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
        # widget -> (field widget -> getter/setter/validators)
        self.field_getter: dict[FieldWidget, dict[QWidget, callable]] = dict()
        self.field_setter: dict[FieldWidget, dict[QWidget, callable]] = dict()
        self.validator_functions: dict[
            FieldWidget, dict[QWidget, list[tuple[callable, callable]]]
        ] = dict()


class DialogProperties(FieldProperties):
    def __init__(self):
        super().__init__()
        self.dialog = None


class ViewProperties:
    def __init__(self):
        super().__init__()
        self.context_menu_list: dict[QAbstractItemView, list[ContextMenuDict]] = dict()
        # columns: (header, getter, optional setter)
        self.columns: dict[QAbstractItemModel, list[tuple[str, callable, callable | None]]] = dict()
        self.models: set[ItemModel] = set()
        self.views: set[ItemViewType] = set()
