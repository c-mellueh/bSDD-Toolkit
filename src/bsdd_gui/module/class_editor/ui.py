from __future__ import annotations
from PySide6.QtWidgets import QApplication, QWidget

from bsdd_gui.resources.icons import get_icon
from . import trigger
from bsdd_parser import BsddClass
from bsdd_gui.presets.ui_presets.label_tags_input import TagInput
from bsdd_gui.module.ifc_helper.data import IfcHelperData


class IfcTagInput(TagInput):
    def __init__(self, *args, **kwargs):
        classes = IfcHelperData.get_classes()
        class_names = [c["code"] for c in classes]
        super().__init__(*args, allowed=class_names, **kwargs)


from .qt import ui_ClassEditor


class ClassEditor(QWidget, ui_ClassEditor.Ui_ClassEditor):
    def __init__(self, bsdd_class: BsddClass):
        self.bsdd_class = bsdd_class
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
