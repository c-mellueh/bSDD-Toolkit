from PySide6.QtWidgets import QWidget

from bsdd_gui.module import logging


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        from .qt.ui_Widget import Ui_Logging

        self.ui = Ui_Logging()
        self.ui.setupUi(self)
        logging.trigger.settings_widget_created(self)
