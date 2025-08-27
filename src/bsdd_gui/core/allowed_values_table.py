from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty, BsddProperty
from bsdd_gui.module.allowed_values_table import ui

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.class_property_editor.ui import ClassPropertyEditor


def connect_signals(
    allowed_values_table: Type[tool.AllowedValuesTable],
    main_window: Type[tool.MainWindow],
    class_property_editor: Type[tool.ClassPropertyEditor],
):
    def test(widget: ClassPropertyEditor):
        for table_widget in allowed_values_table.get_widgets():
            if widget.bsdd_class_property == table_widget.bsdd_property:
                allowed_values_table.append_new_value(table_widget)
                return

    class_property_editor.signaller.new_value_requested.connect(test)
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


def reset_views(allowed_values_table: Type[tool.AllowedValuesTable], project: Type[tool.Project]):
    for view in allowed_values_table.get_widgets():
        allowed_values_table.reset_view(view)


def remove_table(view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTable]):
    model = allowed_values_table.get_model(view.bsdd_property)
    if model:
        allowed_values_table.remove_model(model)
