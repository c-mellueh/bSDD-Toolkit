from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget
from PySide6.QtCore import QAbstractItemModel
from bsdd_gui.resources.icons import get_icon
from . import trigger

class ClassTreeModel(QAbstractItemModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
