from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialogButtonBox
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget
from bsdd_json import BsddClassProperty
from . import trigger
from .qt.ui_Window import Ui_PropertyWindow


class ClassPropertyCreator(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_button = self.button_box.addButton("Create", QDialogButtonBox.ActionRole)


class ClassPropertyEditor(FieldWidget, Ui_PropertyWindow):
    closed = Signal()

    def __init__(self, bsdd_class_property: BsddClassProperty, *args, mode="edit", **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mode = mode  # edit or new
        self.bsdd_data = bsdd_class_property
        trigger.widget_created(self)

    def enterEvent(self, event):
        trigger.update_window(self)
        return super().enterEvent(event)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)
