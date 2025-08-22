from __future__ import annotations
from PySide6.QtWidgets import QApplication, QTreeView
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree import ui
    from bsdd_parser.models import BsddClass


def connect_signals(class_tree: Type[tool.ClassTree], main_window: Type[tool.MainWindow]):
    class_tree.connect_signals()


def connect_view(view: ui.ClassView, class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    class_tree.register_widget(view)
    bsdd_dictionary = project.get()

    view.setModel(class_tree.create_model(bsdd_dictionary))
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)

    sel_model = view.selectionModel()
    sel_model.currentChanged.connect(lambda s, d: class_tree.on_current_changed(view, s, d))


def reset_views(class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    for view in class_tree.get_widgets():
        class_tree.reset_view(view)


def connect_to_main_window(class_tree: Type[tool.ClassTree], main_window: Type[tool.MainWindow]):
    model = main_window.get_class_view().model().sourceModel()
    class_tree.add_column_to_table(model, "Name", lambda a: a.Name)
    class_tree.add_column_to_table(model, "Code", lambda a: a.Code)
    class_tree.add_column_to_table(model, "Status", lambda a: a.Status)
    class_tree.signaller.selection_changed.connect(
        lambda v, n: (
            main_window.set_active_class(n) if v == main_window.get_class_view() else None
        )
    )
