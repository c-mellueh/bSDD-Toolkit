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


def register_fields(widget: BaseWidget, widget_Tool: Type[tool.WidgetTool]):
    widget.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget, widget_tool: Type[tool.WidgetTool], util: Type[tool.Util]):
    widget_tool.add_validator(
        widget,
        widget.le_code,
        lambda v, w,: widget_tool.is_code_valid(v, w),
        lambda w, v: util.set_invalid(w, not v),
    )


def connect_widget(widget: BaseWidget, widget_tool: Type[tool.WidgetTool]):
    widget_tool.connect_widget_signals(widget)
