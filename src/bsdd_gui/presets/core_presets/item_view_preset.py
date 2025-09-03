from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor.ui import ClassPropertyEditor

if TYPE_CHECKING:
    from bsdd_gui.presets import tool_presets as tool
    from bsdd_gui.presets.ui_presets import ItemViewType


def connect_signals(item_view_handler: Type[tool.ItemViewTool]):
    item_view_handler.connect_internal_signals()


def retranslate_ui(item_view_handler: Type[tool.ItemViewTool]):
    pass


def register_view(view: ItemViewType, item_view_handler: Type[tool.ItemViewTool]):
    item_view_handler.register_view(view)


def add_columns_to_view(view: ItemViewType, item_view_handler: Type[tool.ItemViewTool]):
    sort_model, model = item_view_handler.create_model(None)
    item_view_handler.add_column_to_table(
        model, "Value", lambda av: av.Value, item_view_handler.set_value
    )
    item_view_handler.add_column_to_table(
        model, "Code", lambda av: av.Code, item_view_handler.set_code
    )
    item_view_handler.add_column_to_table(
        model, "Description", lambda av: av.Description, item_view_handler.set_description
    )
    item_view_handler.add_column_to_table(
        model, "SortNumber", lambda av: av.SortNumber, item_view_handler.set_sort_number
    )
    item_view_handler.add_column_to_table(
        model, "OwnedUri", lambda av: av.OwnedUri, item_view_handler.set_owned_uri
    )
    view.setModel(sort_model)


def add_context_menu_to_view(view: ItemViewType, item_view_handler: Type[tool.ItemViewTool]):
    item_view_handler.clear_context_menu_list(view)
    item_view_handler.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("AllowedValuesTable", "Delete"),
        lambda: item_view_handler.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )


def connect_view(view: ItemViewType, item_view_handler: Type[tool.ItemViewTool]):
    item_view_handler.connect_view_signals(view)


def create_context_menu(
    view: ItemViewType, pos: QPoint, item_view_handler: Type[tool.ItemViewTool]
):
    bsdd_allowed_values = item_view_handler.get_selected(view)
    menu = item_view_handler.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def remove_view(view: ItemViewType, item_view_handler: Type[tool.ItemViewTool]):
    item_view_handler.remove_model(view.model().sourceModel())
