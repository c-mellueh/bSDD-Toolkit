from __future__ import annotations
from PySide6.QtWidgets import QApplication, QWidget, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtCore import QCoreApplication, Qt

from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser import BsddClass
from bsdd_gui.presets.ui_presets.label_tags_input import TagInput
from bsdd_gui.module.ifc_helper.data import IfcHelperData
from PySide6.QtCore import QRect


class IfcTagInput(TagInput):
    def __init__(self, *args, **kwargs):
        classes = IfcHelperData.get_classes()
        class_names = [c["code"] for c in classes]
        super().__init__(*args, allowed=class_names, **kwargs)


from .qt import ui_ClassEditor


class ClassEditor(QWidget, ui_ClassEditor.Ui_ClassEditor):
    def __init__(self, bsdd_class: BsddClass):
        self.bsdd_data = bsdd_class
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(get_icon())
        trigger.class_editor_created(self)

    # Open / Close windows
    def closeEvent(self, event):

        pass
        # result = trigger.close_event(event)

    def paintEvent(self, event):
        super().paintEvent(event)


class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(get_icon())
        # Create button box
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.button_box)
        self.setLayout(self._layout)
        self.resize(680, 750)
        self._editor_widget: ClassEditor = None
        self.new_button = self.button_box.addButton("Ok", QDialogButtonBox.ActionRole)
        # Prevent pressing Enter/Return from auto-activating this button
        self.new_button.setAutoDefault(False)
        self.new_button.setDefault(False)

    def paintEvent(self, event):
        return super().paintEvent(event)
