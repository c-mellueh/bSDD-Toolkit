from PySide6.QtCore import QModelIndex, Qt, Signal
from PySide6.QtWidgets import QStyledItemDelegate, QTableWidget, QWidget


class PsetTableWidget(QTableWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)