from __future__ import annotations
from PySide6.QtWidgets import QApplication, QTableView
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_table import ui
    from bsdd_parser.models import BsddClass


def connect_signals(property_table: Type[tool.PropertyTable], main_window: Type[tool.MainWindow]):
    pass


def connect_view(
    view: ui.PropertyTable,
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
):
    property_table.register_view(view)
    model = property_table.create_model()
    view.setModel(model)
    sel_model = view.selectionModel()
    sel_model.currentChanged.connect(lambda s, d: property_table.on_current_changed(view, s, d))


def reset_views(property_table: Type[tool.PropertyTable], project: Type[tool.Project]):
    for view in property_table.get_views():
        property_table.reset_view(view)


def connect_to_main_window(
    property_table: Type[tool.PropertyTable], main_window: Type[tool.MainWindow]
):
    model = main_window.get_property_view().model().sourceModel()
    property_view = main_window.get_property_view()
    property_table.add_column_to_table(model, "Name", lambda a: a.Code)
    property_table.add_column_to_table(model, "Datatype", property_table.get_datatype)
    property_table.add_column_to_table(model, "Unit", property_table.get_units)
    property_table.add_column_to_table(model, "Value", property_table.get_allowed_values)
    property_table.add_column_to_table(model, "Optional", lambda a: a.IsRequired)
    property_table.signaller.selection_changed.connect(
        lambda v, n: (main_window.set_active_property(n) if v == property_view else None)
    )
    main_window.signaller.active_pset_changed.connect(
        lambda c: property_table.reset_view(property_view)
    )
