from __future__ import annotations
from PySide6.QtWidgets import QApplication,QTreeView
from typing import Type,TYPE_CHECKING
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_tree import ui


def connect_signals(class_tree: Type[tool.ClassTree]):
    class_tree.connect_signals()
    class_tree.signaller.active_class_changed.connect(lambda c:print(c.Name))


def connect_view(view: ui.ClassView, class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    class_tree.register_view(view)
    bsdd_dictionary = project.get()
    model = class_tree.create_model(bsdd_dictionary)
    view.setModel(model)
    view.setSelectionBehavior(QTreeView.SelectRows)
    view.setSelectionMode(QTreeView.ExtendedSelection)
    view.setAlternatingRowColors(True)

    sel_model = view.selectionModel()    
    # sel_model.selectionChanged.connect(lambda s,d: class_tree.on_selection_changed(view,s,d))
    sel_model.currentChanged.connect(lambda s,d: class_tree.on_current_changed(view,s,d))


def reset_views(class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    for tree_view in class_tree.get_views():
        connect_view(tree_view, class_tree, project)
