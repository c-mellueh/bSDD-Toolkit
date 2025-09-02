from PySide6.QtWidgets import QTreeView, QTableView, QListView
from typing import TypeAlias


class TreeItemView(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: object = None


class TableItemView(QTableView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: object = None


ItemViewType: TypeAlias = TreeItemView | TableItemView
