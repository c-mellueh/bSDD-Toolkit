from __future__ import annotations
from bsdd_parser import BsddClassProperty
from typing import TYPE_CHECKING, Type
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_editor import ui


def open_edit_window(
    bsdd_property: BsddClassProperty,
    parent_widget: QWidget | None,
    property_editor: Type[tool.PropertyEditor],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
):
    if parent_widget is None:
        parent_widget = main_window.get()
    if window := property_editor.get_window(bsdd_property):
        if window.isHidden():
            window.close()
            window = property_editor.create_edit_widget(
                bsdd_property,
                parent_widget,
            )
    else:
        window = property_editor.create_edit_widget(
            bsdd_property,
            parent_widget,
        )
    window.show()
    window.activateWindow()
    window.showNormal()


def connect_signals(
    property_editor: Type[tool.PropertyEditor],
    class_property_editor: Type[tool.ClassPropertyEditor],
):
    property_editor.connect_internal_signals()
    class_property_editor.signaller.property_widget_requested.connect(
        property_editor.request_window
    )


def register_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditor],
):
    property_editor.register_widget(widget)
    property_editor.connect_widget_to_internal_signals(widget)


def add_fields_to_widget(widget: ui.PropertyEditor, property_editor: Type[tool.PropertyEditor]):
    property_editor.register_basic_field(widget, widget.le_code, "Code")
    property_editor.register_basic_field(widget, widget.le_name, "Name")
    property_editor.register_basic_field(widget, widget.te_description, "Definition")
    property_editor.register_basic_field(widget, widget.te_description, "Description")
    property_editor.register_basic_field(widget, widget.ti_units, "Units")
    property_editor.register_basic_field(widget, widget.cb_datatype, "DataType")
    property_editor.register_basic_field(widget, widget.cb_value_kind, "PropertyValueKind")
    property_editor.register_basic_field(widget, widget.cb_status, "Status")
