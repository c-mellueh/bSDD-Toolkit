from PySide6.QtWidgets import QWidget
from typing import TypeAlias


class BaseWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bsdd_data: object = None
