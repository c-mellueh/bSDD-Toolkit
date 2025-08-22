from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtCore import QAbstractItemModel


class ColumnHandlerProperties:
    def __init__(self):
        super().__init__()
        self.columns: dict[QAbstractItemModel, list[tuple[str, callable]]] = dict()


class ViewHandlerProperties:
    def __init__(self):
        super().__init__()
        self.widgets = set()


class ClassTreeProperties(
    ViewHandlerProperties,
    ColumnHandlerProperties,
):
    pass
