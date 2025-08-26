from __future__ import annotations
from PySide6.QtWidgets import QApplication, QTableView
from typing import Type, TYPE_CHECKING
from PySide6.QtCore import QModelIndex

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_table import ui
    from bsdd_parser.models import BsddClass


def connect_signals(
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
    property_set_table: Type[tool.PropertySetTable],
):

    pass


def connect_view(
    view: ui.PropertyTable,
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
):
    def emit_info_requested(index: QModelIndex):
        index = view.model().mapToSource(index)
        bsdd_class_property = index.internalPointer()
        if not bsdd_class_property:
            return
        property_table.signaller.property_info_requested.emit(bsdd_class_property)

    property_table.register_widget(view)
    model = property_table.create_model()
    view.setModel(model)
    sel_model = view.selectionModel()
    sel_model.currentChanged.connect(lambda s, d: property_table.on_current_changed(view, s, d))
    view.doubleClicked.connect(emit_info_requested)


def reset_views(property_table: Type[tool.PropertyTable], project: Type[tool.Project]):
    for view in property_table.get_widgets():
        property_table.reset_view(view)


def connect_to_main_window(
    property_table: Type[tool.PropertyTable], main_window: Type[tool.MainWindow]
):

    def reset_property(new_pset_name: str):
        """
        if the class changes this function checks if the new class has a propertySet with the same name as the old class and selects it
        """
        active_prop = main_window.get_active_property()
        if active_prop is None:
            return
        active_class = main_window.get_active_class()
        property_list = property_table.filter_properties_by_pset(active_class, new_pset_name)
        code_dict = {p.Code: p for p in property_list}
        if active_prop.Code in code_dict:
            new_property = code_dict[active_prop.Code]
            row_index = property_table.get_row_of_property(property_view, new_property)
        else:
            row_index = 0
        property_table.select_row(property_view, row_index)

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
    main_window.signaller.active_pset_changed.connect(reset_property)
