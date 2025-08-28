from __future__ import annotations

from PySide6.QtCore import (
    QAbstractTableModel,
    QSortFilterProxyModel,
    QModelIndex,
    Qt,
    Signal,
)
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets.label_tags_input import TagInput
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Window import Ui_PropertyWindow


class UnitTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class ConnectedPropertyTag(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class ContryTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class ReplacedObjectTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class ReplacingObjectTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class SubdivisionTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)
