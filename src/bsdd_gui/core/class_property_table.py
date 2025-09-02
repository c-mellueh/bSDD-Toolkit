from __future__ import annotations
from PySide6.QtWidgets import QApplication, QTableView
from typing import Type, TYPE_CHECKING
from PySide6.QtCore import QModelIndex
from bsdd_parser.utils import bsdd_class_property as cp_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_property_table import ui
    from bsdd_parser.models import BsddClass


def connect_signals(
    property_table: Type[tool.ClassPropertyTable],
    class_property_editor: Type[tool.ClassPropertyEditor],
):
    property_table.connect_internal_signals()
    class_property_editor.signaller.new_class_property_created.connect(
        lambda *_: property_table.reset_views()
    )


def retranslate_ui(property_table: Type[tool.ClassPropertyTable]):
    pass


def register_view(view: ui.ClassPropertyTable, property_table: Type[tool.ClassPropertyTable]):
    property_table.register_view(view)


def add_columns_to_view(view: ui.ClassPropertyTable, property_table: Type[tool.ClassPropertyTable]):

    sort_model, model = property_table.create_model(None)
    property_table.add_column_to_table(model, "Name", lambda a: a.Code)
    property_table.add_column_to_table(model, "Datatype", cp_utils.get_datatype)
    property_table.add_column_to_table(model, "Unit", cp_utils.get_units)
    property_table.add_column_to_table(model, "Values", property_table.get_allowed_values)
    property_table.add_column_to_table(model, "Is Required", lambda a: a.IsRequired)
    view.setModel(sort_model)


def add_context_menu_to_view(
    view: ui.ClassPropertyTable, property_table: Type[tool.ClassPropertyTable]
):
    pass  # TODO


def connect_view(
    view: ui.ClassPropertyTable,
    property_table: Type[tool.ClassPropertyTable],
    main_window: Type[tool.MainWindow],
):
    def emit_info_requested(index: QModelIndex):
        index = view.model().mapToSource(index)
        bsdd_class_property = index.internalPointer()
        if not bsdd_class_property:
            return
        property_table.signaller.property_info_requested.emit(bsdd_class_property)

    property_table.connect_view_signals(view)
    view.doubleClicked.connect(emit_info_requested)


def reset_views(property_table: Type[tool.ClassPropertyTable], project: Type[tool.Project]):
    for view in property_table.get_widgets():
        property_table.reset_view(view)


def connect_to_main_window(
    property_table: Type[tool.ClassPropertyTable], main_window: Type[tool.MainWindow]
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
        property_table.select_row(property_view, row_index or 0)

    property_view = main_window.get_property_view()

    property_table.signaller.selection_changed.connect(
        lambda v, n: (main_window.set_active_property(n) if v == property_view else None)
    )
    main_window.signaller.active_pset_changed.connect(
        lambda c: property_table.reset_view(property_view)
    )
    main_window.signaller.active_pset_changed.connect(reset_property)
