# src/bsdd_gui/widgets/details_panel.py
from PySide6.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton

class DetailsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.ctrl = None
        self.node = None
        self.name = QLineEdit()
        self.code = QLineEdit()
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self._apply)

        lay = QFormLayout(self)
        lay.addRow("Name", self.name)
        lay.addRow("Code", self.code)
        lay.addRow(self.btn_apply)

    def set_controller(self, ctrl): self.ctrl = ctrl
    def clear(self): self.node = None; self.name.clear(); self.code.clear()

    def show_node(self, node):
        self.node = node
        self.name.setText(getattr(node.obj, "name", getattr(node.obj, "Name", "")) or "")
        self.code.setText(getattr(node.obj, "code", getattr(node.obj, "Code", "")) or "")

    def _apply(self):
        if not self.ctrl or not self.node: return
        self.ctrl.rename(self.node.obj, self.name.text())
        self.ctrl.set_code(self.node.obj, self.code.text())
