from __future__ import annotations
from bsdd_json import BsddClassProperty, BsddProperty
from typing import TYPE_CHECKING, Type
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QCoreApplication
from bsdd_json.utils import bsdd_class_property as cp_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.property_editor_widget import ui


def connect_signals(
    property_editor: Type[tool.PropertyEditorWidget],
    class_property_editor: Type[tool.ClassPropertyEditorWidget],
    project: Type[tool.Project],
):
    property_editor.connect_internal_signals()
    class_property_editor.signals.edit_bsdd_property_requested.connect(
        property_editor.request_widget
    )
    class_property_editor.signals.create_bsdd_property_requested.connect(
        property_editor.request_new_property
    )

    property_editor.signals.new_property_created.connect(project.signals.property_added.emit)


def retranslate_ui(property_editor: Type[tool.PropertyEditorWidget]):
    pass  # TODO


def create_widget(
    bsdd_property: BsddClassProperty,
    parent_widget: QWidget | None,
    property_editor: Type[tool.PropertyEditorWidget],
    main_window: Type[tool.MainWindowWidget],
):
    if parent_widget is None:
        parent_widget = main_window.get()
    property_editor.show_widget(bsdd_property, parent_widget)


def create_dialog(
    blueprint: dict,
    parent_widget: QWidget,
    property_editor: Type[tool.PropertyEditorWidget],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
    util: Type[tool.Util],
):
    # create_virtual Property
    code = QCoreApplication.translate("ClassPropertyEditor", "New Code")
    existing_names = cp_utils.get_property_code_dict(project.get()).keys()
    code = util.get_unique_name(code, existing_names)
    bsdd_property = property_editor.generate_virtual_property(code, blueprint)
    bsdd_property._set_parent(project.get())

    parent_widget = parent_widget if parent_widget is None else main_window.get()
    dialog = property_editor.create_dialog(bsdd_property, parent_widget)
    text = QCoreApplication.translate("ClassPropertyEditor", "Create New Property")
    dialog.setWindowTitle(text)

    if dialog.exec():
        project.get().Properties.append(bsdd_property)
        property_editor.signals.new_property_created.emit(bsdd_property)
        property_editor.signals.dialog_accepted.emit(dialog)
    else:
        property_editor.signals.dialog_declined.emit(dialog)


def register_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditorWidget],
):
    property_editor.register_widget(widget)
    widget.tv_allowed_values.model().sourceModel().bsdd_data = widget.bsdd_data


def register_fields(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditorWidget],
    allowed_values_table: Type[tool.AllowedValuesTableView],
    relationship_editor: Type[tool.RelationshipEditorWidget],
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

    relationship_editor.init_widget(widget.relationship_widget, widget.bsdd_data, mode="live")
    widget.pb_new_value.clicked.connect(
        lambda w=widget: allowed_values_table.append_new_value(widget.tv_allowed_values)
    )

    if widget.bsdd_data.Description:
        widget.cb_description.setChecked(True)
    property_editor.update_description_visiblility(widget)


def register_validators(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditorWidget],
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


def connect_widget(
    widget: ui.PropertyEditor,
    property_editor: Type[tool.PropertyEditorWidget],
    allowed_values_table: Type[tool.AllowedValuesTableView],
):
    property_editor.connect_widget_signals(widget)
    widget.closed.connect(
        lambda w=widget: allowed_values_table.unregister_view(w.tv_allowed_values)
    )


# TODO: add tablevalue add/remove function
