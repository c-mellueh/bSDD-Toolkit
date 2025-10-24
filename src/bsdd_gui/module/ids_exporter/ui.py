from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, QModelIndex, Qt, Signal
from PySide6.QtWidgets import QWidget, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem, QPalette, QIcon
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget,BaseWidget
from bsdd_json import BsddClassProperty
from . import trigger
from bsdd_gui import tool
from .qt.ui_Widget import Ui_Form


class IdsDialog(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   
        self.button_box.addButton("Create", QDialogButtonBox.ActionRole)    

class IdsWidget(FieldWidget,Ui_Form):
    def __init__(self,data, *args, **kwargs):
        self.bsdd_data = data
        super().__init__(*args, **kwargs)    
        self.setupUi(self)
        self.fw_output.section = "paths"
        self.fw_output.option = "ids"
        self.fw_output.load_path()
        trigger.widget_created(self)
