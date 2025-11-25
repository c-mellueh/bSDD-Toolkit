from __future__ import annotations
from PySide6.QtCore import QCoreApplication, QModelIndex
from typing import TYPE_CHECKING, Type, Literal
from bsdd_json.utils import property_utils as prop_utils
from bsdd_gui.module.ids_exporter import constants
import json
import os
import ifctester
from ifctester.facet import Property as PropertyFacet
from ifctester.facet import Entity as EntityFacet
from ifctester.facet import Classification as ClassificationFacet
from ifctester.facet import Restriction
from ifctester.ids import Specification
from bsdd_gui.resources import icons
import qtawesome as qta

import datetime

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.ids_exporter import ui, model_views, models
    from bsdd_json import BsddClass, BsddClassProperty, BsddDictionary
    from bsdd_gui.module.class_tree_view.models import ClassTreeModel as CTM
    from bsdd_gui.tool.ids_exporter import BasicSettingsDict, MetadataDict, PsetDict, SettingsDict


def connect_to_main_window(
    ids_exporter: Type[tool.IdsExporter],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action(
        None, "Ids Exporter", lambda: ids_exporter.request_dialog(project.get(), main_window.get())
    )
    ids_exporter.set_action(main_window.get(), "open_window", action)


def retranslate_ui(ids_exporter: Type[tool.IdsExporter], main_window: Type[tool.MainWindowWidget]):
    action = ids_exporter.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("IDSExport", "Graph View"))


def connect_signals(
    widget_tool: Type[tool.IdsExporter],
    ids_class: Type[tool.IdsClassView],
    ids_property: Type[tool.IdsPropertyView],
):
    widget_tool.connect_internal_signals()
    ids_class.connect_internal_signals()
    ids_property.connect_internal_signals()


def create_widget(data: BsddDictionary, parent, widget_tool: Type[tool.IdsExporter]):
    widget: ui.IdsWidget = widget_tool.show_widget(data, parent)


def create_dialog(data: BsddDictionary, parent, dialog_tool: Type[tool.IdsExporter]):
    dialog = dialog_tool.create_dialog(data, parent)
    text = QCoreApplication.translate("IdsExport", "IDS Exporter")
    dialog.setWindowTitle(text)
    widget = dialog_tool.get_widget()
    model: models.ClassTreeModel = widget.tv_classes.model().sourceModel()
    model.beginResetModel()
    model.bsdd_data = data
    model.endResetModel()
    geom = dialog.geometry()
    dialog.setGeometry(geom.x(), geom.y(), 1600, 900)
    if dialog.exec():
        dialog_tool.sync_to_model(dialog._widget, data)
        dialog_tool.signals.dialog_accepted.emit(dialog)
    else:
        dialog_tool.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.IdsWidget, widget_tool: Type[tool.IdsExporter]):
    widget_tool.register_widget(widget)
    widget.dt_date.hide_toggle_switch()
    widget.dt_date.set_now()
    widget.dt_date.dt_edit.setDisplayFormat("yyyy-MM-dd")

    widget.fw_output.file_format = constants.IDS_FILETYPE
    widget.fw_output.section = "paths"
    widget.fw_output.option = "ids"
    widget.fw_output.title = "get IDS-Export Path"

    widget.pb_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
    widget.pb_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
    widget.pb_import.setText("")
    widget.pb_export.setText("")
    widget.fw_output.load_path()


def register_fields(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    appdata: Type[tool.Appdata],
    util: Type[tool.Util],
):
    def _getter(name, data_type: Literal["string", "list", "bool"] = "string"):
        if data_type == "string":
            return appdata.get_string_setting("ids", name)
        elif data_type == "list":
            return appdata.get_list_setting("ids", name)
        elif data_type == "bool":
            return appdata.get_bool_setting("ids", name)

    def _setter(name, value):
        appdata.set_setting("ids", name, value)

    def _is_not_empty(value, widget):
        if value is None:
            return False
        if isinstance(value, datetime.datetime):
            return True
        if isinstance(value, list):
            return bool(value)
        return bool(value.strip())

    # Check for Classification
    widget_tool.register_field_getter(widget, widget.cb_clsf, lambda _: _getter("classif", "bool"))
    widget_tool.register_field_setter(widget, widget.cb_clsf, lambda _, v: _setter("classif", v))
    widget_tool.register_field_listener(widget, widget.cb_clsf)

    # Inherit to Subclasses
    widget_tool.register_field_getter(widget, widget.cb_inh, lambda _: _getter("inherit", "bool"))
    widget_tool.register_field_setter(widget, widget.cb_inh, lambda _, v: _setter("inherit", v))
    widget_tool.register_field_listener(widget, widget.cb_inh)

    # Title
    widget_tool.register_field_getter(widget, widget.le_title, lambda _: _getter("title"))
    widget_tool.register_field_setter(widget, widget.le_title, lambda _, v: _setter("title", v))
    widget_tool.register_field_listener(widget, widget.le_title)
    widget_tool.add_validator(widget, widget.le_title, _is_not_empty, util.set_valid)

    # Description
    widget_tool.register_field_getter(widget, widget.le_desc, lambda _: _getter("desc"))
    widget_tool.register_field_setter(widget, widget.le_desc, lambda _, v: _setter("desc", v))
    widget_tool.register_field_listener(widget, widget.le_desc)
    widget_tool.add_validator(widget, widget.le_desc, _is_not_empty, util.set_valid)

    # Author
    widget_tool.register_field_getter(widget, widget.le_author, lambda _: _getter("author"))
    widget_tool.register_field_setter(widget, widget.le_author, lambda _, v: _setter("author", v))
    widget_tool.register_field_listener(widget, widget.le_author)
    widget_tool.add_validator(widget, widget.le_author, _is_not_empty, util.set_valid)

    # Milestone
    widget_tool.register_field_getter(widget, widget.le_miles, lambda _: _getter("milestone"))
    widget_tool.register_field_setter(widget, widget.le_miles, lambda _, v: _setter("milestone", v))
    widget_tool.register_field_listener(widget, widget.le_miles)
    widget_tool.add_validator(widget, widget.le_miles, _is_not_empty, util.set_valid)

    # Purpose
    widget_tool.register_field_getter(widget, widget.le_purpose, lambda _: _getter("purpose"))
    widget_tool.register_field_setter(widget, widget.le_purpose, lambda _, v: _setter("purpose", v))
    widget_tool.register_field_listener(widget, widget.le_purpose)
    widget_tool.add_validator(widget, widget.le_purpose, _is_not_empty, util.set_valid)

    # Version
    widget_tool.register_field_getter(widget, widget.le_version, lambda _: _getter("version"))
    widget_tool.register_field_setter(widget, widget.le_version, lambda _, v: _setter("version", v))
    widget_tool.register_field_listener(widget, widget.le_version)
    widget_tool.add_validator(widget, widget.le_version, _is_not_empty, util.set_valid)

    # Copyright
    widget_tool.register_field_getter(widget, widget.le_copyr, lambda _: _getter("copyright"))
    widget_tool.register_field_setter(widget, widget.le_copyr, lambda _, v: _setter("copyright", v))
    widget_tool.register_field_listener(widget, widget.le_copyr)
    widget_tool.add_validator(widget, widget.le_copyr, _is_not_empty, util.set_valid)

    # Ifc-Version
    widget_tool.register_field_getter(widget, widget.ti_ifc_vers, lambda _: _getter("ifc", "list"))
    widget_tool.register_field_setter(widget, widget.ti_ifc_vers, lambda _, v: _setter("ifc", v))
    widget_tool.register_field_listener(widget, widget.ti_ifc_vers)
    widget_tool.add_validator(widget, widget.ti_ifc_vers, _is_not_empty, util.set_valid)

    # Date
    widget_tool.register_field_getter(widget, widget.dt_date, lambda _: _getter("date"))
    widget_tool.register_field_setter(widget, widget.dt_date, lambda _, v: _setter("date", v))
    widget_tool.register_field_listener(widget, widget.dt_date)
    widget_tool.add_validator(widget, widget.dt_date, _is_not_empty, util.set_valid)

    # Datatype
    widget_tool.register_field_getter(widget, widget.cb_datatype, lambda _: _getter("datatype"))
    widget_tool.register_field_setter(
        widget, widget.cb_datatype, lambda _, v: _setter("datatype", v)
    )
    widget_tool.register_field_listener(widget, widget.cb_datatype)
    widget_tool.add_validator(widget, widget.cb_datatype, _is_not_empty, util.set_valid)


def register_validators(widget, widget_tool: Type[tool.IdsExporter], util: Type[tool.Util]):
    pass


def connect_widget(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    ids_class: Type[tool.IdsClassView],
    main_window: Type[tool.MainWindowWidget],
):
    widget.cb_prop.hide()
    widget.cb_pset.hide()
    worker, thread, dialog = widget_tool.count_properties_with_progress(
        widget, widget.bsdd_data.Classes, inline_parent=widget.widget_prop
    )
    widget._count_worker = worker
    widget._count_thread = thread
    widget._count_dialog = dialog
    thread.finished.connect(lambda: setattr(widget, "_count_worker", None))
    thread.finished.connect(lambda: setattr(widget, "_count_thread", None))
    thread.finished.connect(lambda: setattr(widget, "_count_dialog", None))
    worker.finished.connect(lambda: widget_tool.fill_pset_combobox(widget))
    widget_tool.connect_widget_signals(widget)
    class_view = widget.tv_classes
    ids_class.connect_settings_signals(widget, class_view)


def register_class_view(view: model_views.ClassView, ids_class_view: Type[tool.IdsClassView]):
    ids_class_view.register_view(view)


def register_property_view(
    view: model_views.PropertyView, ids_property_view: Type[tool.IdsPropertyView]
):
    ids_property_view.register_view(view)


def add_columns_to_class_view(
    view: model_views.ClassView,
    ids_class: Type[tool.IdsClassView],
    ids_exporter: Type[tool.IdsExporter],
):
    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_class = index.internalPointer()
        ids_class.set_checkstate(bsdd_class, value)

    data = ids_exporter.get_data()
    proxy_model, model = ids_class.create_model(data)
    ids_class.add_column_to_table(model, "Name", lambda a: a.Name)
    ids_class.add_column_to_table(model, "Code", lambda a: a.Code)
    ids_class.add_column_to_table(model, "Export", ids_class.get_checkstate, set_checkstate)
    view.setModel(proxy_model)


def add_columns_to_property_view(
    view: model_views.PropertyView,
    ids_property: Type[tool.IdsPropertyView],
    ids_exporter: Type[tool.IdsExporter],
):

    data = ids_exporter.get_data()
    proxy_model, model = ids_property.create_model(data)

    def set_checkstate(model: CTM, index: QModelIndex, value: bool):
        bsdd_class = index.internalPointer()
        ids_property.set_checkstate(model, bsdd_class, value)

    ids_property.add_column_to_table(model, "Name", ids_property._get_name)
    ids_property.add_column_to_table(model, "Code", ids_property._get_code)
    ids_property.add_column_to_table(
        model, "Export", lambda cp: ids_property.get_checkstate(model, cp), set_checkstate
    )

    view.setModel(proxy_model)


def connect_class_view(view: model_views.ClassView, ids_class: Type[tool.IdsClassView]):
    ids_class.connect_view_signals(view)


def connect_property_view(
    view: model_views.PropertyView,
    ids_property: Type[tool.IdsPropertyView],
    ids_class: Type[tool.IdsClassView],
):

    def update_property_view(
        class_view: model_views.ClassView,
        data: BsddClass,
    ):
        dialog: ui.IdsDialog = class_view.window()
        property_view = dialog._widget.tv_properties
        proxy_model: models.SortModel = property_view.model()
        model = proxy_model.sourceModel()
        model.beginResetModel()
        model.bsdd_data = data
        model.endResetModel()

    ids_class.signals.selection_changed.connect(update_property_view)
    ids_property.connect_view_signals(view)


def export_settings(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    class_view: Type[tool.IdsClassView],
    property_view: Type[tool.IdsPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    # Create Dict
    class_dict: dict[str, bool] = class_view.get_check_dict()
    property_dict: PsetDict = property_view.get_check_dict()
    settings_dict: BasicSettingsDict = widget_tool.get_settings(widget)
    ids_metadata: MetadataDict = widget_tool.get_ids_metadata(widget)
    full_dict: SettingsDict = {
        "class_settings": class_dict,
        "property_settings": property_dict,
        "settings": settings_dict,
        "ids_metadata": ids_metadata,
    }

    # Set Path
    text = QCoreApplication.translate("IDSExport", "Export IDS settings")
    old_path = appdata.get_path(constants.IDS_APPDATA)
    new_path = popups.get_save_path(constants.SETTINGS_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.IDS_APPDATA, new_path)

    # Write Json
    with open(new_path, "w") as file:
        json.dump(full_dict, file)


def import_settings(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    class_view: Type[tool.IdsClassView],
    property_view: Type[tool.IdsPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    # Handle Path
    old_path = appdata.get_path(constants.IDS_APPDATA)
    text = QCoreApplication.translate("IDSExport", "Import IDS settings")
    new_path = popups.get_open_path(constants.SETTINGS_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.IDS_APPDATA, new_path)

    # Read Settings
    with open(new_path, "r") as file:
        full_dict: SettingsDict = json.load(file)
    class_dict = full_dict.get("class_settings", {})
    property_dict = full_dict.get("property_settings", {})
    settings_dict = full_dict.get("settings", {})
    ids_metadata = full_dict.get("ids_metadata", {})

    # Fill Fields and Checkstates
    class_view.set_check_dict(class_dict, widget.tv_classes)
    property_view.set_check_dict(property_dict, widget.tv_properties)
    widget_tool.set_settings(widget, settings_dict)
    widget_tool.set_ids_metadata(widget, ids_metadata)
    pass


def export_ids(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    class_view: Type[tool.IdsClassView],
    property_view: Type[tool.IdsPropertyView],
    main_window: Type[tool.MainWindowWidget],
    popups: Type[tool.Popups],
):
    class_settings = class_view.get_check_dict()
    property_settings = property_view.get_check_dict()
    base_settings = widget_tool.get_settings(widget)
    metadata_settings = widget_tool.get_ids_metadata(widget)

    out_path = widget.fw_output.get_path()
    template_path = widget_tool.get_template()
    ifc_version = metadata_settings.get("ifc_versions", ["IFC4X3_ADD2"])
    bsdd_dict = widget.bsdd_data
    ids = ifctester.ids.open(template_path)
    base_spec = ids.specifications[0]
    base_requirement: PropertyFacet = base_spec.requirements[0]
    base_requirement.propertySet = base_settings.get("main_pset", "")
    base_requirement.baseName = base_settings.get("main_property", "")
    base_restriction = base_requirement.value
    base_restriction.options = {"enumeration": [c.Code for c in bsdd_dict.Classes]}
    base_spec.ifcVersion = ifc_version

    ids.info["title"] = metadata_settings.get("title", ids.info.get("title"))
    ids.info["description"] = metadata_settings.get("description", ids.info.get("description"))
    ids.info["author"] = metadata_settings.get("author", ids.info.get("author"))
    ids.info["milestone"] = metadata_settings.get("milestone", ids.info.get("milestone"))
    ids.info["purpose"] = metadata_settings.get("purpose", ids.info.get("purpose"))
    ids.info["version"] = metadata_settings.get("version", ids.info.get("version"))
    ids.info["copyright"] = metadata_settings.get("copyright", ids.info.get("copyright"))

    # If Inherit is Checked it will build the class settings dict exclude subclasses of unchecked classes
    if base_settings["inherit"]:
        class_settings = widget_tool.build_inherited_checkstate_dict(
            bsdd_dict.Classes, class_settings
        )

    input = sorted(bsdd_dict.Classes, key=lambda x: x.Code)
    worker, thread, dialog = widget_tool.create_specification_with_progress(
        ids,
        input,
        base_settings,
        class_settings,
        property_settings,
        bsdd_dict,
        ifc_version,
        main_window.get(),
    )
    widget._specification_worker = worker
    widget._specification_thread = thread
    widget._specification_dialog = dialog

    def _export():
        ids.to_xml(out_path)
        popups.create_info_popup(
            f"{len(ids.specifications)} Specifications created.",
            "IDS Export Done!",
            "IDS Export Done!",
            parent=main_window.get(),
        )

    thread.finished.connect(_export)
    thread.finished.connect(lambda: setattr(widget, "_specification_worker", None))
    thread.finished.connect(lambda: setattr(widget, "_specification_dialog", None))
    thread.finished.connect(lambda: setattr(widget, "_specification_thread", None))

