from PySide6.QtWidgets import QWidget

from bsdd_gui.resources.icons import get_icon


class SettingsWidget(QWidget):
    def __init__(self, *args, **kwargs):
        from .qt.ui_Widget import Ui_Settings

        super().__init__(*args, **kwargs)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.setWindowIcon(get_icon())

        from . import trigger

        trigger.settings_widget_created(self)
