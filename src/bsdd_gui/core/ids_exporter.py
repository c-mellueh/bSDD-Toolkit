from __future__ import annotations
from PySide6.QtCore import QCoreApplication, QModelIndex, QTimer
from typing import TYPE_CHECKING, Type
from bsdd_gui.module.ids_exporter import constants
import json
import re
import qtawesome as qta
from bsdd_gui.presets.ui_presets.waiting import stop_waiting_widget
import logging

import datetime

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.tool.ids_exporter import (
        BasicSettingsDict,
        MetadataDict,
        PsetDict,
        SettingsDict,
        PayLoadDict,
    )
    from bsdd_gui.module.ids_exporter import ui
    from ifctester.ids import Ids


def connect_to_main_window(
    ids_exporter: Type[tool.IdsExporter],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing

    action = main_window.add_action(
        None, "Ids Exporter", lambda: ids_exporter.request_widget(project.get(), main_window.get())
    )
    ids_exporter.set_action(main_window.get(), "open_window", action)


def retranslate_ui(ids_exporter: Type[tool.IdsExporter], main_window: Type[tool.MainWindowWidget]):
    action = ids_exporter.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("IDSExport", "IDS Exporter"))


def connect_signals(widget_tool: Type[tool.IdsExporter]):
    widget_tool.connect_internal_signals()


def create_widget(
    widget_tool: Type[tool.IdsExporter],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    widget: ui.IdsWidget = widget_tool.show_widget(project.get(), main_window.get())
    text = QCoreApplication.translate("IdsExport", "IDS Exporter")
    widget.setWindowTitle(text)



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
    widget.fw_output.load_path()


def register_fields(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
):

    widget_tool.register_appdata_field(widget, widget.cb_clsf, "ids", "classif", "bool")
    widget_tool.register_appdata_field(widget, widget.cb_type_objects, "ids", "type_obj", "bool")
    widget_tool.register_appdata_field(widget, widget.cb_inh, "ids", "inherit", "bool")
    widget_tool.register_appdata_field(widget, widget.le_title, "ids", "title", "string")
    widget_tool.register_appdata_field(widget, widget.le_desc, "ids", "desc", "string")
    widget_tool.register_appdata_field(widget, widget.le_author, "ids", "author", "string")
    widget_tool.register_appdata_field(widget, widget.le_miles, "ids", "milestone", "string")
    widget_tool.register_appdata_field(widget, widget.le_purpose, "ids", "purpose", "string")
    widget_tool.register_appdata_field(widget, widget.le_version, "ids", "version", "string")
    widget_tool.register_appdata_field(widget, widget.le_copyr, "ids", "copyright", "string")
    widget_tool.register_appdata_field(widget, widget.ti_ifc_vers, "ids", "ifc", "list")
    widget_tool.register_appdata_field(widget, widget.dt_date, "ids", "date", "string")
    widget_tool.register_appdata_field(widget, widget.cb_datatype, "ids", "datatype", "string")

    widget_tool.register_appdata_field(
        widget, widget.cb_string, "ids", "string", "string", "IFCTEXT"
    )
    widget_tool.register_appdata_field(
        widget, widget.cb_boolean, "ids", "le_boolean", "string", "IFCBOOLEAN"
    )
    widget_tool.register_appdata_field(
        widget, widget.cb_integer, "ids", "integer", "string", "IFCINTEGER"
    )
    widget_tool.register_appdata_field(widget, widget.cb_real, "ids", "real", "string", "IFCREAL")
    widget_tool.register_appdata_field(
        widget, widget.cb_character, "ids", "character", "string", "IFCLABEL"
    )
    widget_tool.register_appdata_field(
        widget, widget.cb_time, "ids", "time", "string", "IFCDATETIME"
    )
    widget_tool.sync_from_model(widget, widget.bsdd_data)


def register_validators(widget:ui.IdsWidget, widget_tool: Type[tool.IdsExporter], util: Type[tool.Util]):
    def _is_not_empty(value, _):
        if value is None:
            return False
        if isinstance(value, datetime.datetime):
            return True
        if isinstance(value, list):
            return bool(value)
        return bool(value.strip())

    def _check_mail(value, widget):
        if not _is_not_empty(value, widget):
            return False
        return bool(re.match(r"[^@]+@[^\.]+\..+", value))

    widget_tool.add_validator(widget, widget.le_title, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.le_desc, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.le_author, _check_mail, util.set_valid)
    widget_tool.add_validator(widget, widget.le_miles, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.le_purpose, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.le_version, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.le_copyr, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.ti_ifc_vers, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.dt_date, _is_not_empty, util.set_valid)
    widget_tool.add_validator(widget, widget.cb_datatype, _is_not_empty, util.set_valid)


def connect_widget(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    pp_class_view: Type[tool.PPClassView],
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
    class_view = widget.property_picker.tv_classes
    widget.cb_inh.toggled.connect(lambda cs: pp_class_view.request_set_inheritance(cs,class_view))





def export_settings(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    # Create Dict
    class_tree = widget.property_picker.tv_classes
    property_tree = widget.property_picker.tv_properties
    class_dict: dict[str, bool] = pp_class_view.get_checked_classes(class_tree)
    property_dict: PsetDict = pp_property_view.get_check_dict(property_tree)
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
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    new_path = popups.get_save_path(constants.SETTINGS_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.APPDATA_OPTION, new_path)

    # Write Json
    with open(new_path, "w") as file:
        json.dump(full_dict, file)


def import_settings(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    # Handle Path
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    text = QCoreApplication.translate("IDSExport", "Import IDS settings")
    new_path = popups.get_open_path(constants.SETTINGS_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.APPDATA_OPTION, new_path)

    # Read Settings
    with open(new_path, "r") as file:
        full_dict: SettingsDict = json.load(file)
    class_dict = full_dict.get("class_settings", {})
    property_dict = full_dict.get("property_settings", {})
    settings_dict = full_dict.get("settings", {})
    ids_metadata = full_dict.get("ids_metadata", {})

    # Fill Fields and Checkstates
    class_tree = widget.property_picker.tv_classes
    property_tree = widget.property_picker.tv_properties
    pp_class_view.set_check_dict(class_dict, class_tree)
    pp_property_view.set_check_dict(property_dict, property_tree)
    widget_tool.set_settings(widget, settings_dict)
    widget_tool.set_ids_metadata(widget, ids_metadata)
    pass


def export_ids(
    widget: ui.IdsWidget,
    widget_tool: Type[tool.IdsExporter],
    popups: Type[tool.Popups],
    util: Type[tool.Util],
    project: Type[tool.Project],
    property_picker: Type[tool.PropertyPicker],
):
    widget_tool.sync_to_model(widget, widget.bsdd_data)
    bsdd_dict = project.get()
    specs = list(property_picker.get_properties().specs.values())
    checked_classes = property_picker.get_checked_classes(specs, bsdd_dict)
    property_settings = property_picker.get_checked_properties(specs, bsdd_dict)
    base_settings = widget_tool.get_settings(widget)
    metadata_settings = widget_tool.get_ids_metadata(widget)

    title = QCoreApplication.translate("IDSExport", "Export IDS")

    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(title)
    waiting_widget.set_title("Load Data")

    setup_worker, setup_thread = widget_tool.create_setup_thread(
        widget, checked_classes, property_settings, base_settings, metadata_settings
    )

    def _start_specification(payload: PayLoadDict):
        waiting_widget.set_title("Build IDS")
        logging.info("Create Specification")
        create_worker, creator_thread, creator_dialog = widget_tool.create_build_thread(
            payload, waiting_widget
        )
        creator_thread.finished.connect(lambda: _export(payload["ids"], payload["out_path"]))
        creator_thread.start()

    def _show_error(exc: Exception):
        stop_waiting_widget(waiting_worker)
        t = QCoreApplication.translate("IDSExport", "Export Error")
        popups.create_info_popup(str(exc), t, t, parent=widget)

    def _dispatch_specification(payload: PayLoadDict):
        # queue execution on the main thread (mw affinity)
        QTimer.singleShot(0, widget, lambda: _start_specification(payload))

    def _export(ids: Ids, out_path: str):
        logging.info("Creation Done!")
        logging.info("Start Export!")

        write_worker, write_thread = widget_tool.create_write_thread(ids, out_path)
        waiting_widget.set_title("Write IDS")
        write_worker.finished.connect(
            lambda: popups.create_info_popup(
                f"{len(ids.specifications)} Specifications created.",
                "IDS Export Done!",
                "IDS Export Done!",
                parent=widget,
            )
        )
        write_worker.finished.connect(lambda: stop_waiting_widget(waiting_worker))
        write_worker.error.connect(_show_error)
        logging.info("Export Done!")
        write_thread.start()

    setup_worker.finished.connect(_dispatch_specification)
    setup_worker.error.connect(_show_error)
    setup_thread.start()
