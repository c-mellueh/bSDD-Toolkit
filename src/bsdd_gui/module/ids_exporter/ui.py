from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget, BaseWidget
from bsdd_json import BsddClassProperty, BsddDictionary
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form


class IdsDialog(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._widget: IdsWidget
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            event.accept()  # Konsumieren, nichts tun
            return
        super().keyPressEvent(event)


class IdsWidget(FieldWidget, Ui_Form):
    def __init__(self, data: BsddDictionary, *args, **kwargs):
        super().__init__(data, *args, **kwargs)
        self.bsdd_data: BsddDictionary
        self.setupUi(self)

        trigger.widget_created(self)
