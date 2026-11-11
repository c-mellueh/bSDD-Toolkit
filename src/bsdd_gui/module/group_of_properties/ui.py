from bsdd_gui.presets.ui_presets import FieldWidget
from . import trigger
from .qt.ui_Widget import Ui_Form
from .qt.ui_Settings import Ui_Form as Ui_SettingsForm
from PySide6.QtWidgets import QWidget


class GopWidget(FieldWidget, Ui_Form):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.widget_created(self)


class SettingsWidget(QWidget, Ui_SettingsForm):
    """Settings page: code prefix of predefined property sets and automatic creation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.settings_created(self)
