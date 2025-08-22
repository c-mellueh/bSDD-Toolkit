from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
from bsdd_gui.module.property_set_table import ui
from PySide6.QtWidgets import QApplication, QListView


def connect_view(
    view: ui.PsetTableView,
    pset_table: Type[tool.PropertySetTable],
    project: Type[tool.Project],
    main_window: Type[tool.MainWindow],
):

    def test_for_mw(view: ui.PsetTableView, name: str):
        if view == main_window.get_pset_view():
            main_window.set_active_pset(name)

    pset_table.add_column_to_table("Name", lambda a: a)
    pset_table.register_view(view)
    bsdd_dictionary = project.get()
    model = pset_table.create_model(bsdd_dictionary)
    view.setModel(model)
    view.setSelectionBehavior(QListView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QListView.SelectionMode.SingleSelection)
    view.setAlternatingRowColors(True)
    sel_model = view.selectionModel()
    # sel_model.selectionChanged.connect(lambda s,d: class_tree.on_selection_changed(view,s,d))
    sel_model.currentChanged.connect(lambda s, d: pset_table.on_current_changed(view, s, d))
    main_window.signaller.active_class_changed.connect(lambda c: pset_table.reset_view(view))
    pset_table.signaller.selection_changed.connect(test_for_mw)


def reset_views(pset_list: Type[tool.PropertySetTable], project: Type[tool.Project]):
    for view in pset_list.get_views():
        pset_list.reset_view(view)
