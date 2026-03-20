from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_json import BsddClassProperty, BsddProperty
from PySide6.QtCore import QCoreApplication, QPoint
from bsdd_gui.module.class_property_editor_widget.ui import ClassPropertyEditor

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_picker import ui


def connect_signals(property_picker: Type[tool.PropertyPicker]):
    property_picker.connect_internal_signals()


def retranslate_ui(property_picker: Type[tool.PropertyPicker]):
    pass


def register_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker]):
    property_picker.register_widget(widget)


def connect_widget(widget: ui.Widget, property_picker: Type[tool.PropertyPicker]):
    property_picker.connect_widget_signals(widget)

