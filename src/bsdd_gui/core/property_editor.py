from __future__ import annotations
from bsdd_parser import BsddClassProperty, BsddProperty
from typing import TYPE_CHECKING, Type
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QCoreApplication
from bsdd_parser.utils import bsdd_class_property as cp_utils

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
    if window := property_editor.get_widget(bsdd_property):
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
    project: Type[tool.Project],
):
    property_editor.connect_internal_signals()
    class_property_editor.signaller.edit_bsdd_property_requested.connect(
        property_editor.request_widget
    )
    class_property_editor.signaller.create_bsdd_property_requested.connect(
        property_editor.request_new_property
    )

    property_editor.signaller.new_property_created.connect(project.signaller.property_added.emit)


def unregister_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditor],
):
    property_editor.unregister_widget(widget)


def register_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditor],
    allowed_values_table: Type[tool.AllowedValuesTable],
):
    property_editor.register_widget(widget)
    property_editor.connect_widget_to_internal_signals(widget)


def add_fields_to_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditor],
    allowed_values_table: Type[tool.AllowedValuesTable],
    relationship_editor: Type[tool.RelationshipEditor],
):
    property_editor.register_basic_field(widget, widget.le_code, "Code")
    property_editor.register_basic_field(widget, widget.le_name, "Name")
    property_editor.register_basic_field(widget, widget.le_measurement, "MethodOfMeasurement")
    property_editor.register_basic_field(widget, widget.le_example, "Example")
    property_editor.register_basic_field(widget, widget.le_text_format, "TextFormat")
    property_editor.register_basic_field(widget, widget.le_uid, "Uid")
    property_editor.register_basic_field(widget, widget.le_visual_rep, "VisualRepresentationUri")

    property_editor.register_basic_field(widget, widget.te_definition, "Definition")
    property_editor.register_basic_field(widget, widget.te_description, "Description")

    property_editor.register_basic_field(widget, widget.ti_units, "Units")
    property_editor.register_basic_field(
        widget, widget.ti_connect_properties, "ConnectedPropertyCodes"
    )
    property_editor.register_basic_field(widget, widget.ti_countries, "CountriesOfUse")
    property_editor.register_basic_field(
        widget, widget.ti_replacing_objects, "ReplacingObjectCodes"
    )
    property_editor.register_basic_field(widget, widget.ti_replaced_objects, "ReplacedObjectCodes")
    property_editor.register_basic_field(widget, widget.ti_subdivision, "SubdivisionsOfUse")

    property_editor.register_basic_field(widget, widget.cb_datatype, "DataType")
    property_editor.register_basic_field(widget, widget.cb_value_kind, "PropertyValueKind")
    property_editor.register_basic_field(widget, widget.cb_status, "Status")
    property_editor.register_basic_field(widget, widget.cb_country_origin, "CountryOfOrigin")
    property_editor.register_basic_field(widget, widget.cb_creator_iso, "CreatorLanguageIsoCode")
    property_editor.register_basic_field(widget, widget.cb_creator_iso, "DocumentReference")

    property_editor.register_basic_field(widget, widget.de_activation_time, "ActivationDateUtc")
    property_editor.register_basic_field(widget, widget.de_revision_time, "RevisionDateUtc")
    property_editor.register_basic_field(widget, widget.de_deactivation_time, "DeActivationDateUtc")
    property_editor.register_basic_field(widget, widget.de_version_date, "VersionDateUtc")

    property_editor.register_basic_field(widget, widget.sb_version_number, "VersionNumber")

    # Allowed Values Table
    table = allowed_values_table.create_widget(widget.data)
    widget.vl_values.addWidget(table)
    relationship_editor.init_widget(widget.relationship_widget, widget.data, mode="live")
    widget.pb_new_value.clicked.connect(
        lambda w=widget: allowed_values_table.append_new_value(table)
    )

    if widget.data.Description:
        widget.cb_description.setChecked(True)
    property_editor.update_description_visiblility(widget)


def add_validator_functions_to_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditor],
    util: Type[tool.Util],
    project: Type[tool.Project],
):
    property_editor.add_validator(
        widget,
        widget.le_code,
        lambda v, w: property_editor.is_code_valid(v, w, project.get()),
        lambda w, v: util.set_invalid(w, not v),
    )
    property_editor.add_validator(
        widget,
        widget.le_name,
        property_editor.is_name_valid,
        lambda w, v: util.set_invalid(w, not v),
    )
    property_editor.add_validator(
        widget,
        widget.cb_datatype,
        property_editor.is_datatype_valid,
        lambda w, v: util.set_invalid(w, not v),
    )


def create_property_creator(
    blueprint: dict,
    property_editor: Type[tool.PropertyEditor],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    code = QCoreApplication.translate("ClassPropertyEditor", "New Code")
    existing_names = cp_utils.get_property_code_dict(project.get()).keys()
    code = util.get_unique_name(code, existing_names)
    model_dict = dict() if not blueprint else blueprint
    if "Code" not in model_dict:
        model_dict["Code"] = code
    if "Name" not in model_dict:
        model_dict["Name"] = code
    if "DataType" not in model_dict:
        model_dict["DataType"] = "String"
    bsdd_property = BsddProperty.model_validate(model_dict)
    bsdd_property._set_parent(project.get())

    dialog = property_editor.create_create_dialog(bsdd_property, main_window.get())
    widget = dialog._editor_widget
    text = QCoreApplication.translate("ClassPropertyEditor", "Create New Property")
    dialog.setWindowTitle(text)
    if dialog.exec():
        property_editor.sync_to_model(widget, bsdd_property)
        project.get().Properties.append(bsdd_property)
        property_editor.signaller.new_property_created.emit(bsdd_property)
    property_editor.unregister_widget(widget)


# TODO: add tablevalue add/remove function
