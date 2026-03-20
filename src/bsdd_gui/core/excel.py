from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.excel import ui


def connect_signals(excel: Type[tool.Excel]):
    excel.connect_internal_signals()


def retranslate_ui(excel: Type[tool.Excel]):
    pass


def create_widget(data, parent, excel: Type[tool.Excel]):
    excel.show_widget(data, parent)


def register_widget(widget: ui.Widget, excel: Type[tool.Excel]):
    excel.register_widget(widget)


def register_fields(widget: ui.Widget, excel: Type[tool.Excel]):
    excel.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget:ui.Widget, excel: Type[tool.Excel], util: Type[tool.Util]):
    excel.add_validator(
        widget,
        widget.le_code,
        lambda v, w,: excel.is_code_valid(v, w),
        lambda w, v: util.set_invalid(w, not v),
    )


def connect_widget(widget: ui.Widget, excel: Type[tool.Excel]):
    excel.connect_widget_signals(widget)

