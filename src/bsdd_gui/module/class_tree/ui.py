from __future__ import annotations
from PySide6.QtWidgets import QTreeView, QTreeWidget, QWidget

from bsdd_gui.resources.icons import get_icon
from . import trigger

class ClassView(QTreeView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)