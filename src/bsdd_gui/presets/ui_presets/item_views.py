from PySide6.QtWidgets import QTreeView, QTableView
from typing import TypeAlias


class TreeItemView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TableItemView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


ItemViewType: TypeAlias = TreeItemView | TableItemView
