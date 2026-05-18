from __future__ import annotations
from PySide6.QtWidgets import QSizePolicy
from bsdd_gui.presets.ui_presets import FieldWidget
from . import trigger
from .qt.ui_Widget import Ui_Form


class DownloadWidget(FieldWidget, Ui_Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        trigger.widget_created(self)
