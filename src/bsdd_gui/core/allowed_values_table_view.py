from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty, BsddProperty
from bsdd_gui.module.allowed_values_table_view import ui
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_gui.module.class_property_editor_widget.constants import (
    SEPERATOR,
    SEPERATOR_SECTION,
    SEPERATOR_STATUS,
)

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(
    allowed_values_table: Type[tool.AllowedValuesTableView],
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
):
    class_property_editor.signals.new_value_requested.connect(
        allowed_values_table.handle_new_value_request
    )
    allowed_values_table.connect_internal_signals()
    class_property_editor.signals.widget_closed.connect(
        allowed_values_table.remove_view_by_property_editor
    )


def retranslate_ui(allowed_values_table: Type[tool.AllowedValuesTableView]):
    pass


def register_view(
    view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTableView]
):
    allowed_values_table.register_view(view)


def add_columns_to_view(
    view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTableView]
):
    prop: BsddClassProperty | BsddProperty = view.bsdd_data

    sort_model, model = allowed_values_table.create_model(
        prop
    )  # if the widget is enbedded in ui the value needs to be updated on setup
    allowed_values_table.add_column_to_table(
        model, "Value", lambda av: av.Value, lambda model, index, value: allowed_values_table.set_value( index, value)
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


def add_context_menu_to_view(
    view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTableView]
):
    allowed_values_table.clear_context_menu_list(view)
    allowed_values_table.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("AllowedValuesTable", "Delete"),
        lambda: allowed_values_table.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )


def connect_view(
    view: ui.AllowedValuesTable,
    allowed_values_table: Type[tool.AllowedValuesTableView],
    util: Type[tool.Util],
):
    view.setItemDelegateForColumn(0,ui.LiveEditDelegate(parent=view))
    allowed_values_table.connect_view_signals(view)
    util.add_shortcut(
        "Ctrl+V", view, lambda v=view: allowed_values_table.signals.items_pasted.emit(v)
    )


def create_context_menu(
    view: ui.AllowedValuesTable,
    pos: QPoint,
    allowed_values_table: Type[tool.AllowedValuesTableView],
):
    bsdd_allowed_values = allowed_values_table.get_selected(view)
    menu = allowed_values_table.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def remove_view(
    view: ui.AllowedValuesTable, allowed_values_table: Type[tool.AllowedValuesTableView]
):
    allowed_values_table.remove_model(view.model().sourceModel())


def item_paste_event(
    view: ui.AllowedValuesTable,
    allowed_values_table: Type[tool.AllowedValuesTableView],
    util: Type[tool.Util],
    appdata: Type[tool.Appdata],
):
    seperator_text = appdata.get_string_setting(SEPERATOR_SECTION, SEPERATOR)
    seperator_status = appdata.get_bool_setting(SEPERATOR_SECTION, SEPERATOR_STATUS)

    content = util.get_clipboard_content(seperator_text if seperator_status else None)
    model = view.model().sourceModel()
    bsdd_data = model.bsdd_data
    existing_codes = {v.Code.lower() for v in bsdd_data.AllowedValues}
    code_index = allowed_values_table.get_column_names(model).index("Code")

    for line in content:
        if not isinstance(line, list):
            code = dict_utils.slugify(line)
            if code.lower() in existing_codes or not code:
                continue
            else:
                existing_codes.add(code)
            row_count = allowed_values_table.append_new_value(view)
            bsdd_data.AllowedValues[row_count].Code = code
            bsdd_data.AllowedValues[row_count].Value = line
            continue

        if code_index >= len(line):
            if len(line) == 1:
                line.append(dict_utils.slugify(line[0]))
            else:
                continue
        pasted_code = line[code_index]
        if str(pasted_code).lower() in existing_codes:
            continue
        else:
            existing_codes.add(str(pasted_code))

        row_count = allowed_values_table.append_new_value(view)
        for col_index, value in enumerate(line):
            if not isinstance(value, (str, int, float)):
                continue
            if col_index >= allowed_values_table.get_column_count(model):
                continue
            index = model.index(row_count, col_index)
            allowed_values_table.value_setter_functions(model)[col_index](model, index, str(value))
