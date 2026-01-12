from PySide6.QtWidgets import QWidget

from .qt.ui_Settings import Ui_Form
from . import trigger, constants


class SettingsWidget(QWidget, Ui_Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        trigger.settings_created(self)
        self.cb_language.clear()
        self.cb_language.addItems(constants.LANGUAGES)
