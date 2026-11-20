from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
    QProgressBar,
    QMessageBox,
    QSplitter,
    QHeaderView,
    QGroupBox,
)
from PySide6.QtCore import Qt, Signal

from bsdd_gui.resources.icons import get_icon


class ModelcheckWindow(QWidget):
    run_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("IFC Modelcheck (bSDD)"))
        self.resize(850, 650)
        self.setWindowIcon(get_icon())

        layout = QVBoxLayout(self)

        file_box = QGroupBox(self.tr("Files"))
        file_layout = QVBoxLayout(file_box)

        h_ifc = QHBoxLayout()
        h_ifc.addWidget(QLabel(self.tr("IFC Model:")))
        self.ifc_input = QLineEdit()
        self.ifc_btn = QPushButton(self.tr("Browse..."))
        self.ifc_btn.clicked.connect(self._browse_ifc)
        h_ifc.addWidget(self.ifc_input)
        h_ifc.addWidget(self.ifc_btn)
        file_layout.addLayout(h_ifc)

        h_exp = QHBoxLayout()
        h_exp.addWidget(QLabel(self.tr("Excel Report:")))
        self.export_input = QLineEdit()
        self.export_btn = QPushButton(self.tr("Browse..."))
        self.export_btn.clicked.connect(self._browse_export)
        h_exp.addWidget(self.export_input)
        h_exp.addWidget(self.export_btn)
        file_layout.addLayout(h_exp)

        h_ident = QHBoxLayout()
        h_ident.addWidget(QLabel(self.tr("Identifier Property Set:")))
        self.pset_input = QLineEdit()
        self.pset_input.setPlaceholderText("e.g. AllplanAttributes or Common")
        h_ident.addWidget(self.pset_input)
        h_ident.addWidget(QLabel(self.tr("Identifier Property:")))
        self.prop_input = QLineEdit()
        self.prop_input.setPlaceholderText("e.g. BauteilID or Code")
        h_ident.addWidget(self.prop_input)
        file_layout.addLayout(h_ident)

        layout.addWidget(file_box)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        class_box = QGroupBox(self.tr("bSDD Classes & Properties to check"))
        cb_layout = QVBoxLayout(class_box)
        self.class_tree = QTreeWidget()
        self.class_tree.setHeaderLabels([self.tr("Name / Code"), self.tr("Property Set"), self.tr("Data Type")])
        self.class_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        cb_layout.addWidget(self.class_tree)
        splitter.addWidget(class_box)
        layout.addWidget(splitter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.run_button = QPushButton(self.tr("Run Modelcheck"))
        self.run_button.clicked.connect(self.run_clicked)
        self.close_button = QPushButton(self.tr("Close"))
        self.close_button.clicked.connect(self.close)
        btn_layout.addWidget(self.run_button)
        btn_layout.addWidget(self.close_button)
        layout.addLayout(btn_layout)

    def _browse_ifc(self):
        filter_str = "IFC Files (*.ifc *.IFC)"
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Select IFC File"), "", filter_str)
        if path:
            self.ifc_input.setText(path)
            if not self.export_input.text():
                self.export_input.setText(path.rsplit('.', 1)[0] + "_modelcheck.xlsx")

    def _browse_export(self):
        filter_str = "Excel Files (*.xlsx);;BCF Files (*.bcf)"
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Select Export Path"), "", filter_str)
        if path:
            self.export_input.setText(path)

    def retranslateUi(self, widget):
        self.setWindowTitle(self.tr("IFC Modelcheck (bSDD)"))
