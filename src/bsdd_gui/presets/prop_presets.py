from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtCore import QAbstractItemModel
from PySide6.QtGui import QAction
from typing import TypedDict, Callable


class ContextMenuDict(TypedDict):
    label_func: Callable[[], str]  # returns label text for the action
    action_func: Callable[..., None]  # function executed when triggered
    allow_single: bool  # available for single selection
    allow_multi: bool  # available for multi-selection
    require_selection: bool  # only enabled if something is selected
    action: QAction  # actual QAction object


class ColumnHandlerProperties:
    def __init__(self):
        super().__init__()
        self.columns: dict[QAbstractItemModel, list[tuple[str, callable]]] = dict()
        self.model: QAbstractItemModel = None


class ModuleHandlerProperties:
    def __init__(self):
        super().__init__()
        self.actions = dict()


class WidgetHandlerProperties:
    def __init__(self):
        super().__init__()
        self.widgets = set()


class ViewHandlerProperties(WidgetHandlerProperties):
    def __init__(self):
        super().__init__()
        self.context_menu_list: dict[QAbstractItemView, list[ContextMenuDict]] = dict()


class ClassTreeProperties(
    ViewHandlerProperties,
    ColumnHandlerProperties,
):
    pass
