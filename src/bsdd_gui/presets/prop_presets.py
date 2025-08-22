from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtCore import QAbstractItemModel


class ColumnHandlerProperties:
    def __init__(self):
        self.columns: dict[QAbstractItemModel, list[tuple[str, callable]]] = dict()


class ViewHandlerProperties:
    def __init__(self):
        self.views = set()
