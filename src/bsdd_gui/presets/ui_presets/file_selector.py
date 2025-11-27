from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QToolButton
from PySide6.QtCore import QMargins
from typing import Literal
import sys
from PySide6.QtWidgets import QApplication

MODES = Literal["open", "save"]
FILETYPE = "bSDD Project (*.json);;all (*.*)"


class FileSelector(QWidget):
    def __init__(
        self,
        parent=None,
        section: str = "test",
        option: str = "test",
        mode: MODES = "open",
        file_format=FILETYPE,
        title=None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        layout = QHBoxLayout(self)
        self.setLayout(layout)
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))
        self.line_edit = QLineEdit()
        self.layout().addWidget(self.line_edit)
        self.tool_button = QToolButton()
        self.tool_button.setText("...")
        self.layout().addWidget(self.tool_button)

        self.section = section
        self.option = option
        self.mode = mode
        self.file_format = file_format
        self.tool_button.clicked.connect(self.on_button_click)
        self.title = title

    def load_path(self):
        from bsdd_gui.tool import Appdata

        path = Appdata.get_string_setting(self.section, self.option, None)
        if path:
            self.line_edit.setText(path)

    def set_path(self, path: str):
        self.line_edit.setText(path)

    def get_path(self):
        return self.line_edit.text()

    def on_button_click(self):
        from bsdd_gui.tool import Appdata, Popups

        path = Appdata.get_string_setting(self.section, self.option, None)
        path = Popups.get_save_path(self.file_format, self, path, title=self.title)
        if path is not None:
            Appdata.set_setting(self.section, self.option, path)
            self.set_path(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fs = FileSelector("Test", "Test")
    fs.show()
    sys.exit(app.exec())
