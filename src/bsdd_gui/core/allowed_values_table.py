from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty, BsddProperty
from bsdd_gui.module.allowed_values_table import ui
from PySide6.QtCore import QCoreApplication, QPoint

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(
    allowed_values_table: Type[tool.AllowedValuesTable],
    main_window: Type[tool.MainWindow],
    class_property_editor: Type[tool.ClassPropertyEditor],
):

    class_property_editor.signaller.new_value_requested.connect(
        allowed_values_table.handle_new_value_request
    )
    allowed_values_table.signaller.delete_selection_requested.connect(
        allowed_values_table.delete_selection
    )
    pass


def setup_view(view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTable]):
    prop: BsddClassProperty | BsddProperty = view.bsdd_property

    allowed_values_table.register_widget(view)
    sort_model = allowed_values_table.create_model(prop)
    model = sort_model.sourceModel()

    allowed_values_table.add_column_to_table(
        model, "Value", lambda av: av.Value, allowed_values_table.set_value
    )
    allowed_values_table.add_column_to_table(
        model, "Code", lambda av: av.Code, allowed_values_table.set_code
    )
    allowed_values_table.add_column_to_table(
        model, "Description", lambda av: av.Description, allowed_values_table.set_description
    )
    allowed_values_table.add_column_to_table(
        model, "SortNumber", lambda av: av.SortNumber, allowed_values_table.set_sort_number
    )
    allowed_values_table.add_column_to_table(
        model, "OwnedUri", lambda av: av.OwnedUri, allowed_values_table.set_owned_uri
    )
    view.setModel(sort_model)
    allowed_values_table.connect_view_signals(view)


def add_context_menu_to_view(
    view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTable]
):
    allowed_values_table.clear_context_menu_list(view)
    allowed_values_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("AllowedValuesTable", "Delete"),
        lambda: allowed_values_table.signaller.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )


def create_context_menu(
    view: ui.AllowedValuesTable, pos: QPoint, allowed_values_table: Type[tool.AllowedValuesTable]
):
    bsdd_allowed_values = allowed_values_table.get_selected(view)
    menu = allowed_values_table.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def reset_views(allowed_values_table: Type[tool.AllowedValuesTable], project: Type[tool.Project]):
    for view in allowed_values_table.get_widgets():
        allowed_values_table.reset_view(view)


def remove_table(view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTable]):
    model = allowed_values_table.get_model(view.bsdd_property)
    if model:
        allowed_values_table.remove_model(model)
