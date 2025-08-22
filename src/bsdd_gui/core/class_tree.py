from __future__ import annotations
from PySide6.QtWidgets import QApplication, QTreeView
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree import ui
    from bsdd_parser.models import BsddClass


def connect_signals(class_tree: Type[tool.ClassTree], main_window: Type[tool.MainWindow]):
    def test_for_mw(view: ui.ClassView, bsdd_class: BsddClass):
        if view == main_window.get_class_view():
            main_window.set_active_class(bsdd_class)
    class_tree.add_column_to_table("Name", lambda a: a.Name)
    class_tree.add_column_to_table("Code", lambda a: a.Code)
    class_tree.add_column_to_table("Status", lambda a: a.Status)
    class_tree.connect_signals()
    class_tree.signaller.selection_changed.connect(test_for_mw)


def connect_view(view: ui.ClassView, class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    class_tree.register_view(view)
    bsdd_dictionary = project.get()

    view.setModel(class_tree.create_model(bsdd_dictionary))
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)

    sel_model = view.selectionModel()
    sel_model.currentChanged.connect(lambda s, d: class_tree.on_current_changed(view, s, d))


def reset_views(class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    for view in class_tree.get_views():
        class_tree.reset_view(view)
