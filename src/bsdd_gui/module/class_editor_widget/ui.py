from __future__ import annotations
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QToolButton,
)
from PySide6.QtCore import QCoreApplication, Qt, QEvent
import qtawesome as qta
from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_json import BsddClass
from bsdd_gui.presets.ui_presets import TagInput, FieldWidget, BaseDialog
from bsdd_gui.module.ifc_helper.data import IfcHelperData
from PySide6.QtCore import QRect


class IfcTagInput(TagInput):
    def __init__(self, *args, **kwargs):
        classes = IfcHelperData.get_classes()
        class_names = [c["code"] for c in classes]
        super().__init__(*args, allowed=class_names, **kwargs)


from .qt import ui_ClassEditor


class ClassEditor(FieldWidget, ui_ClassEditor.Ui_ClassEditor):

    def __init__(self, bsdd_class: BsddClass, *args, **kwargs):
        super().__init__(bsdd_class, *args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(get_icon())
        self.bsdd_data: BsddClass
        self._init_definition_toolbutton()

        trigger.widget_created(self)

    # Open / Close windows
    def closeEvent(self, event):

        pass
        # result = trigger.close_event(event)

    def paintEvent(self, event):
        super().paintEvent(event)

    def _init_definition_toolbutton(self) -> None:
        """Place a helper button inside the definition text edit."""
        self._definition_toolbutton = QToolButton(self.te_definition.viewport())
        self._definition_toolbutton.setIcon(qta.icon("mdi6.creation-outline"))
        self._definition_toolbutton.setAutoRaise(True)
        self._definition_toolbutton.setCursor(Qt.PointingHandCursor)
        self.te_definition.viewport().installEventFilter(self)
        self.te_definition.textChanged.connect(self._sync_definition_toolbutton)
        self._position_definition_toolbutton()
        self._sync_definition_toolbutton()

    def _position_definition_toolbutton(self) -> None:
        margin = 6
        self._definition_toolbutton.move(margin, margin)

    def _sync_definition_toolbutton(self) -> None:
        is_empty = self.te_definition.toPlainText() == ""
        self._definition_toolbutton.setVisible(is_empty)

    def eventFilter(self, obj, event):
        if obj is self.te_definition.viewport() and event.type() == QEvent.Resize:
            self._position_definition_toolbutton()
        return super().eventFilter(obj, event)


class EditDialog(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowIcon(get_icon())
        # Create button box
        self.setLayout(self._layout)
        self.resize(680, 750)
        self.new_button = self.button_box.addButton("Ok", QDialogButtonBox.ActionRole)
        # Prevent pressing Enter/Return from auto-activating this button
        self.new_button.setAutoDefault(False)
        self.new_button.setDefault(False)

    def paintEvent(self, event):
        return super().paintEvent(event)
