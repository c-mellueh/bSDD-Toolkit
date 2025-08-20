from __future__ import annotations
from PySide6.QtWidgets import QApplication,QTableView
from typing import Type,TYPE_CHECKING
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_table import ui
    from bsdd_parser.models import BsddClass


def connect_signals(property_table: Type[tool.PropertyTable], main_window: Type[tool.MainWindow]):
    pass

def connect_view(view: ui.PropertyTable, property_table: Type[tool.PropertyTable],main_window:Type[tool.MainWindow]):
    property_table.register_view(view)
    model = property_table.create_model()
    view.setModel(model)
    view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QTableView.SelectionMode.ExtendedSelection)
    view.setAlternatingRowColors(True)

    sel_model = view.selectionModel()    
    # sel_model.selectionChanged.connect(lambda s,d: property_table.on_selection_changed(view,s,d))
    sel_model.currentChanged.connect(lambda s,d: property_table.on_current_changed(view,s,d))
    main_window.signaller.active_pset_changed.connect(lambda c: property_table.reset_view(view))


def reset_views(property_table: Type[tool.PropertyTable], project: Type[tool.Project]):
    for view in property_table.get_views():
        property_table.reset_view(view)