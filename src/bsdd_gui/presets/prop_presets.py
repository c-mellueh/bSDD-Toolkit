from PySide6.QtWidgets import QAbstractItemView, QWidget
from PySide6.QtCore import QAbstractItemModel
from PySide6.QtGui import QAction
from typing import TypedDict, Callable, TypeAlias
from .view_presets import TreeItemView, TableItemView

ItemViewType: TypeAlias = TreeItemView | TableItemView


class ContextMenuDict(TypedDict):
    label_func: Callable[[], str]  # returns label text for the action
    action_func: Callable[..., None]  # function executed when triggered
    allow_single: bool  # available for single selection
    allow_multi: bool  # available for multi-selection
    require_selection: bool  # only enabled if something is selected
    action: QAction  # actual QAction object


class ModuleHandlerProperties:
    def __init__(self):
        super().__init__()
        self.actions = dict()


class FieldHandlerProperties:
    def __init__(self):
        super().__init__()
        self.field_getter: dict[QWidget, dict[QWidget, callable]] = (
            dict()
        )  # getter function for widgets of Window
        self.field_setter: dict[QWidget, dict[QWidget, callable]] = (
            dict()
        )  # getter function for widgets of Window
        self.validator_functions: dict[QWidget, dict[QWidget, tuple[callable, callable]]] = dict()


class WidgetHandlerProperties(FieldHandlerProperties):
    def __init__(self):
        super().__init__()
        self.widgets = set()


class ViewHandlerProperties(WidgetHandlerProperties):
    def __init__(self):
        super().__init__()
        self.context_menu_list: dict[QAbstractItemView, list[ContextMenuDict]] = dict()
        self.columns: dict[QAbstractItemModel, list[tuple[str, callable]]] = dict()
        self.model: QAbstractItemModel = None
        self.models = dict(object, QAbstractItemModel)
        self.views: set[ItemViewType] = set()
