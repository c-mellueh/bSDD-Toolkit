from __future__ import annotations
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtCore import QCoreApplication, Qt

from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser import BsddClass
from bsdd_gui.presets.ui_presets import TagInput, BaseWidget, BaseDialog
from bsdd_gui.module.ifc_helper.data import IfcHelperData
from PySide6.QtCore import QRect


class IfcTagInput(TagInput):
    def __init__(self, *args, **kwargs):
        classes = IfcHelperData.get_classes()
        class_names = [c["code"] for c in classes]
        super().__init__(*args, allowed=class_names, **kwargs)


from .qt import ui_ClassEditor


class ClassEditor(BaseWidget, ui_ClassEditor.Ui_ClassEditor):

    def __init__(self, bsdd_class: BsddClass, *args, **kwargs):
        super().__init__(bsdd_class, *args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(get_icon())
        self.bsdd_data: BsddClass
        trigger.widget_created(self)

    # Open / Close windows
    def closeEvent(self, event):

        pass
        # result = trigger.close_event(event)

    def paintEvent(self, event):
        super().paintEvent(event)


class EditDialog(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(get_icon())
        # Create button box
        self.setLayout(self._layout)
        self.resize(680, 750)
        self._widget: ClassEditor = None
        self.new_button = self.button_box.addButton("Ok", QDialogButtonBox.ActionRole)
        # Prevent pressing Enter/Return from auto-activating this button
        self.new_button.setAutoDefault(False)
        self.new_button.setDefault(False)

    def paintEvent(self, event):
        return super().paintEvent(event)
