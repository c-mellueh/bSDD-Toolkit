from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout
from PySide6.QtCore import Qt, QCoreApplication
from bsdd_gui.resources.icons import get_icon


class NewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(get_icon())
        # Create button box
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        new_text = QCoreApplication.translate("Project", "Create New Project")
        self.new_button = self.button_box.addButton(new_text, QDialogButtonBox.ActionRole)

        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self.button_box)
        self.setLayout(self._layout)
