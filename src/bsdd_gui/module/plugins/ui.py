from PySide6.QtWidgets import QFormLayout, QWidget

from bsdd_gui.module import plugins


class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QFormLayout())

        plugins.trigger.settings_widget_created(self)
