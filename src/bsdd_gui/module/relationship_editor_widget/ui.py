from __future__ import annotations

from typing import Literal
from . import trigger
from .qt.ui_Widget import Ui_Form
from .qt.ui_Settings import Ui_Form as Ui_SettingsForm
from bsdd_gui.presets.ui_presets import BaseWidget


class RelationshipWidget(BaseWidget, Ui_Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data = None
        self.mode: Literal["dialog"] | Literal["live"] = None
        self.setupUi(Form=self)

    def closeEvent(self, event):
        self.closed.emit()
        return super().closeEvent(event)


class SettingsWidget(BaseWidget, Ui_SettingsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.settings_created(self)
