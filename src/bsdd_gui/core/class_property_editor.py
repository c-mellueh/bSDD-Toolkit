from __future__ import annotations

from typing import TYPE_CHECKING, Type
from bsdd_parser import BsddClassProperty
from bsdd_gui.module.class_property_editor.constants import (
    SEPERATOR_SECTION,
    SEPERATOR,
    SEPERATOR_STATUS,
)
from PySide6.QtCore import QCoreApplication
from bsdd_gui.module.class_property_editor import ui
from bsdd_parser.utils import bsdd_class_property as cp_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_editor import ui as property_editor_ui


def unregister_widget(
    widget: ui.ClassPropertyEditor, class_property_editor: Type[tool.ClassPropertyEditor]
):
    class_property_editor.unregister_widget(widget)


def register_widget(
    widget: ui.ClassPropertyEditor, class_property_editor: Type[tool.ClassPropertyEditor]
):
    class_property_editor.register_widget(widget)
    class_property_editor.connect_widget_to_internal_signals(widget)


def add_fields_to_widget(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditor],
    allowed_values_table: Type[tool.AllowedValuesTable],
    project: Type[tool.Project],
):
    class_property_editor.register_basic_field(widget, widget.le_code, "Code")
    class_property_editor.register_basic_field(widget, widget.te_description, "Description")
    class_property_editor.register_basic_field(widget, widget.cb_is_required, "IsRequired")

    ### Property Reference Field
    class_property_editor.register_field_getter(
        widget, widget.le_property_reference, class_property_editor.get_property_reference
    )
    class_property_editor.register_field_setter(
        widget,
        widget.le_property_reference,
        lambda e, v, p=project: class_property_editor.set_property_reference(e, v, p.get()),
    )
    class_property_editor.register_field_listener(widget, widget.le_property_reference)
    table = allowed_values_table.create_widget(widget.bsdd_class_property)
    widget.vl_values.addWidget(table)


def add_validators_to_widget(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditor],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    class_property_editor.add_validator(
        widget,
        widget.le_property_reference,
        lambda v, w, p=project: class_property_editor.is_property_reference_valid(
            v, w.bsdd_class_property, p.get()
        ),
        lambda w, v: util.set_invalid(w, not v),
    )

    class_property_editor.add_validator(
        widget,
        widget.le_property_reference,
        lambda v, w, p=project: class_property_editor.is_property_reference_valid(
            v, w.bsdd_class_property, p.get()
        ),
        lambda f, v, w=widget: class_property_editor.handle_property_reference_button(w, f, v),
    )


def update_property_specific_fields(
    widget: ui.ClassPropertyEditor,
    class_property_editor: Type[tool.ClassPropertyEditor],
    allowed_value_table: Type[tool.AllowedValuesTable],
):
    if not widget:
        return
    class_property_editor.update_description_placeholder(widget)
    class_property_editor.update_allowed_units(widget)
    class_property_editor.update_value_view(widget)
    allowed_value_table.reset_view(allowed_value_table.get_view_from_property_editor(widget))


def open_edit_window(
    bsdd_class_property: BsddClassProperty,
    class_property_editor: Type[tool.ClassPropertyEditor],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
):
    if window := class_property_editor.get_window(bsdd_class_property):
        if window.isHidden():
            window.close()
            window = class_property_editor.create_edit_widget(
                bsdd_class_property, main_window.get(), bsdd_dictionary=project.get()
            )
    else:
        window = class_property_editor.create_edit_widget(
            bsdd_class_property, main_window.get(), bsdd_dictionary=project.get()
        )
    window.show()
    window.activateWindow()
    window.showNormal()


def splitter_settings_accepted(
    class_property_editor: Type[tool.ClassPropertyEditor], appdata: Type[tool.Appdata]
):
    widget = class_property_editor.get_splitter_settings_widget()
    is_seperator_activated = class_property_editor.get_splitter_settings_checkstate(widget)
    text = class_property_editor.get_splitter_settings_text(widget)
    text = text.replace("\\n", "\n")
    text = text.replace("\\t", "\t")

    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR, text)
    appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, is_seperator_activated)
    if not text:
        appdata.set_setting(SEPERATOR_SECTION, SEPERATOR_STATUS, False)


def connect_signals(
    class_property_editor: Type[tool.ClassPropertyEditor],
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
    property_editor: Type[tool.PropertyEditor],
):
    property_table.signaller.property_info_requested.connect(
        class_property_editor.show_property_info
    )
    class_property_editor.connect_internal_signals()
    main_window.signaller.new_property_requested.connect(
        class_property_editor.signaller.create_new_class_property_requested.emit
    )

    def handle_field_changed(parent_widget: property_editor_ui.PropertyEditor, field):
        for widget in class_property_editor.get_widgets():
            bsdd_class_property: BsddClassProperty = widget.bsdd_class_property
            internal_prop = cp_utils.get_internal_property(bsdd_class_property)
            if not internal_prop:
                continue

            if parent_widget.bsdd_property == internal_prop:
                class_property_editor.request_property_specific_redraw(widget)

    property_editor.signaller.field_changed.connect(handle_field_changed)


def create_class_property_creator(
    class_property_editor: Type[tool.ClassPropertyEditor],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
    property_set_table: Type[tool.PropertySetTable],
):
    code = QCoreApplication.translate("ClassPropertyEditor", "New Code")
    bsdd_class = main_window.get_active_class()
    bsdd_class_property = BsddClassProperty.model_validate(
        {"Code": code, "PropertyCode": code, "PropertyUri": None, "IsRequired": True}
    )

    if not main_window.get_active_class():
        return
    property_set = main_window.get_active_pset()
    if not property_set:
        return

    is_temporary_pset = property_set_table.is_temporary_pset(bsdd_class, property_set)
    bsdd_class_property.PropertySet = property_set
    bsdd_class_property._set_parent(bsdd_class)

    dialog = class_property_editor.create_create_dialog(
        bsdd_class_property, main_window.get(), project.get()
    )
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassPropertyEditor", "Create New Class Property")
    dialog.setWindowTitle(text)
    if dialog.exec():
        class_property_editor.sync_to_model(widget, bsdd_class_property)
        bsdd_class_property.parent().ClassProperties.append(bsdd_class_property)
        class_property_editor.signaller.new_class_property_created.emit(bsdd_class_property)
        if is_temporary_pset:
            property_set_table.remove_temporary_pset(bsdd_class_property.parent(), property_set)
            property_set_table.signaller.model_refresh_requested.emit()
    class_property_editor.unregister_widget(widget)
