from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.iso_export import ui


def connect_signals(iso_export: Type[tool.IsoExport]):
    iso_export.connect_internal_signals()


def retranslate_ui(iso_export: Type[tool.IsoExport]):
    pass


def create_widget(data, parent, iso_export: Type[tool.IsoExport]):
    iso_export.show_widget(data, parent)


def create_dialog(data: object, parent, iso_export: Type[tool.IsoExport]):
    dialog = iso_export.create_dialog(data, parent)
    text = QCoreApplication.translate("Preset", "Example Title")
    dialog.setWindowTitle(text)
    if dialog.exec():
        iso_export.sync_to_model(dialog._widget, data)
        iso_export.signals.dialog_accepted.emit(dialog)
    else:
        iso_export.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    iso_export.register_widget(widget)


def register_fields(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    iso_export.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget:ui.Widget, iso_export: Type[tool.IsoExport], util: Type[tool.Util]):
    iso_export.add_validator(
        widget,
        widget.le_code,
        lambda v, w,: iso_export.is_code_valid(v, w),
        lambda w, v: util.set_invalid(w, not v),
    )


def connect_widget(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    iso_export.connect_widget_signals(widget)

