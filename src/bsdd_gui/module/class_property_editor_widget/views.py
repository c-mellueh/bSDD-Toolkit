from __future__ import annotations

from PySide6.QtCore import (
    QCoreApplication,
    QSortFilterProxyModel,
    QModelIndex,
    Qt,
    Signal,
)

from PySide6.QtWidgets import QWidget, QWidget, QGridLayout, QApplication, QLineEdit, QStyle
from PySide6.QtGui import QStyleHints, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets.label_tags_input import TagInput
from bsdd_gui.resources.icons import get_icon, get_link_icon
from bsdd_parser import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_SplitterSettings import Ui_SplitterSettings


class ValueView(QGridLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ValueTagInput(TagInput):
    def __init__(self, parent=None, placeholder="Add tag…", allowed=None, minimum_le_width=250):
        super().__init__(parent, placeholder, allowed, minimum_le_width)


class SplitterSettings(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ui = Ui_SplitterSettings()
        self.ui.setupUi(self)
        trigger.splitter_settings_created(self)
