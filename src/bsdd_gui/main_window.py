# src/bsdd_gui/main_window.py
from PySide6.QtWidgets import QMainWindow, QFileDialog, QTreeView, QDockWidget, QMessageBox
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
from .models.tree_model import BsddTreeModel
from .widgets.details_panel import DetailsPanel
from .actions.edit_actions import build_edit_actions
from .actions.file_actions import build_file_actions

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BSDD Viewer/Editor")
        self.resize(1200, 800)

        self.tree = QTreeView()
        self.tree.setUniformRowHeights(True)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.setCentralWidget(self.tree)

        self.details = DetailsPanel()
        dock = QDockWidget("Details", self)
        dock.setWidget(self.details)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # empty model initially
        self.model = None

        # menus / actions
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        edit_menu = menubar.addMenu("&Edit")

        build_file_actions(self, file_menu)
        build_edit_actions(self, edit_menu)

        # selection → details binding
        self.tree.selectionModelChanged = False
        self.tree.selectionModelChanged = self.tree.selectionModelChanged if hasattr(self.tree, "selectionModelChanged") else None

    def load_model(self, dictionary_obj, controller):
        """dictionary_obj is your parser root object; controller exposes load/save/edit API."""
        self.model = BsddTreeModel(dictionary_obj, controller)
        self.tree.setModel(self.model)
        self.tree.expandToDepth(1)
        self.tree.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.details.set_controller(controller)

    def _on_selection_changed(self, selected, _deselected):
        idxs = selected.indexes()
        if not idxs:
            self.details.clear()
            return
        # use first column as the representative index
        idx = [i for i in idxs if i.column() == 0][0]
        node = self.model.node_from_index(idx)
        self.details.show_node(node)
