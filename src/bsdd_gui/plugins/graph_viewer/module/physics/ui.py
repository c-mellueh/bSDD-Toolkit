from __future__ import annotations
from bsdd_gui.plugins.graph_viewer.module.settings.ui import _SettingsWidget

from .qt.ui_Widget import Ui_Form
class SettingsWidget(Ui_Form,_SettingsWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

