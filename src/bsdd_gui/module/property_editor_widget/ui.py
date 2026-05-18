from __future__ import annotations
from typing import Literal
from PySide6.QtWidgets import QDialogButtonBox
from bsdd_gui.presets.ui_presets import BaseDialog, FieldWidget
from . import trigger
from .qt.ui_Window import Ui_PropertyWindow


class PropertyCreator(BaseDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Layout
        self.new_button = self.button_box.addButton("Create", QDialogButtonBox.ActionRole)
        self._widget: PropertyEditor


class PropertyEditor(FieldWidget, Ui_PropertyWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.mode: Literal["edit"] | Literal["new"] = None  # edit or new
        trigger.widget_created(self)
