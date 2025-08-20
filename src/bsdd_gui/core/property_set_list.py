from __future__ import annotations

from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from bsdd_gui import tool
from bsdd_gui.module.property_set_list import ui
from PySide6.QtWidgets import QApplication,QListView

def connect_view(view: ui.PsetListView, pset_list: Type[tool.PropertySetList], project: Type[tool.Project]):
    pset_list.register_view(view)
    bsdd_dictionary = project.get()
    model = pset_list.create_model(bsdd_dictionary)
    view.setModel(model)
    view.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QListView.SelectionMode.SingleSelection)
    view.setAlternatingRowColors(True)

    sel_model = view.selectionModel()    
    # sel_model.selectionChanged.connect(lambda s,d: class_tree.on_selection_changed(view,s,d))
    sel_model.currentChanged.connect(lambda s,d: pset_list.on_current_changed(view,s,d))


def reset_views(class_tree: Type[tool.ClassTree], project: Type[tool.Project]):
    for tree_view in class_tree.get_views():
        connect_view(tree_view, class_tree, project)