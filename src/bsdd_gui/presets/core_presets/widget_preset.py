from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

if TYPE_CHECKING:
    from bsdd_gui.presets import tool_presets as tool
    from bsdd_gui.presets.ui_presets.base_widgets import BaseWidget


def connect_signals(widget_tool: Type[tool.WidgetTool]):
    widget_tool.connect_internal_signals()


def retranslate_ui(widget_tool: Type[tool.WidgetTool]):
    pass


def open_widget(data: object, parent, widget_tool: Type[tool.WidgetTool]):
    widget_tool.create_widget(data, parent)


def open_dialog(data: object, parent, dialog_tool: Type[tool.DialogTool]):
    dialog = dialog_tool.create_dialog(data, parent)
    text = QCoreApplication.translate("Preset", "Example Title")
    dialog.setWindowTitle(text)
    if dialog.exec():
        dialog_tool.sync_to_model(dialog._widget, data)
        dialog_tool.signals.dialog_accepted.emit(dialog)
    else:
        dialog_tool.signals.dialog_declined.emit(dialog)


def register_widget(widget: BaseWidget, widget_tool: Type[tool.WidgetTool]):
    widget_tool.register_view(widget)


def add_columns_to_view(view: BaseWidget, widget_tool: Type[tool.WidgetTool]):
    prop: BsddClassProperty | BsddProperty = view.bsdd_data
    sort_model, model = widget_tool.create_model(prop)
    widget_tool.add_column_to_table(model, "Value", lambda av: av.Value, widget_tool.set_value)
    widget_tool.add_column_to_table(model, "Code", lambda av: av.Code, widget_tool.set_code)
    widget_tool.add_column_to_table(
        model, "Description", lambda av: av.Description, widget_tool.set_description
    )
    widget_tool.add_column_to_table(
        model, "SortNumber", lambda av: av.SortNumber, widget_tool.set_sort_number
    )
    widget_tool.add_column_to_table(
        model, "OwnedUri", lambda av: av.OwnedUri, widget_tool.set_owned_uri
    )
    view.setModel(sort_model)


def add_context_menu_to_view(view: BaseWidget, widget_tool: Type[tool.WidgetTool]):
    widget_tool.clear_context_menu_list(view)
    widget_tool.add_context_menu_entry(
        view,
        lambda: QCoreApplication.translate("AllowedValuesTable", "Delete"),
        lambda: widget_tool.signals.delete_selection_requested.emit(view),
        True,
        True,
        True,
    )


def connect_view(view: BaseWidget, widget_tool: Type[tool.WidgetTool]):
    widget_tool.connect_view_signals(view)


def create_context_menu(view: BaseWidget, pos: QPoint, widget_tool: Type[tool.WidgetTool]):
    bsdd_allowed_values = widget_tool.get_selected(view)
    menu = widget_tool.create_context_menu(view, bsdd_allowed_values)
    menu_pos = view.viewport().mapToGlobal(pos)
    menu.exec(menu_pos)


def remove_view(view: BaseWidget, widget_tool: Type[tool.WidgetTool]):
    widget_tool.remove_model(view.model().sourceModel())
