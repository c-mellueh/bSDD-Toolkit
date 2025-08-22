from PySide6.QtWidgets import QApplication, QWidget

from bsdd_gui.resources.icons import get_icon
from . import trigger
from .qt import ui_ClassEditor
from bsdd_parser import BsddClass


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
