from __future__ import annotations

from typing import TYPE_CHECKING, Type
if TYPE_CHECKING:
    from bsdd_gui import tool
from bsdd_gui.module.property_set_list import ui
from PySide6.QtWidgets import QApplication,QListView

def connect_view(view: ui.PsetListView, pset_list: Type[tool.PropertySetList], project: Type[tool.Project],main_window:Type[tool.MainWindow]):
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
    main_window.signaller.active_class_changed.connect(lambda c: pset_list.reset_view(view))


def reset_views(pset_list: Type[tool.PropertySetList], project: Type[tool.Project]):
    for view in pset_list.get_views():
        pset_list.reset_view(view)
