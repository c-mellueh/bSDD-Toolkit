from __future__ import annotations
from PySide6.QtCore import QCoreApplication,QTimer
from typing import TYPE_CHECKING, Type
import qtawesome as qta
from bsdd_gui.module.iso_export import constants
import json
from bsdd_json.utils import class_utils
from bsdd_gui.presets.ui_presets.waiting import stop_waiting_widget


if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.iso_export import ui
    from bsdd_gui.tool.property_picker import PsetDict
    from bsdd_gui.tool.iso_export import SettingsDict
    from bsdd_json import BsddClass

def connect_to_main_window(
    iso_export: Type[tool.IsoExport],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing 
    action = main_window.add_action(
        "menuFile",
        "Export ISO 23386",
        lambda: iso_export.request_widget(
            project.get(),
            main_window.get(),
        ),
        qta.icon("mdi6.file-excel"),

    )
    iso_export.set_action(main_window.get(), "open_window", action)


def connect_signals(iso_export: Type[tool.IsoExport]):
    iso_export.connect_internal_signals()


def retranslate_ui(iso_export: Type[tool.IsoExport],main_window:type[tool.MainWindowWidget]):
    action = iso_export.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("IsoExport", "Export ISO 23386"))



def create_widget(data, parent, iso_export: Type[tool.IsoExport]):
    iso_export.show_widget(data, parent)


def register_widget(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    iso_export.register_widget(widget)
    widget.fw_output.file_format = constants.ISO_FILETYPE
    widget.fw_output.section = "paths"
    widget.fw_output.option = "iso_23386"
    widget.fw_output.title = "get ISO23386-Export Path"

    widget.pb_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
    widget.pb_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
    widget.fw_output.load_path()
    widget.pb_import.clicked.connect(lambda _=False, w=widget: _import_loin(w, iso_export))
    widget.pb_export.clicked.connect(lambda _=False, w=widget: _export_loin(w, iso_export))


def _import_loin(widget: ui.Widget, iso_export: Type[tool.IsoExport]) -> None:
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    from bsdd_gui.tool.loin import Loin

    title = QCoreApplication.translate("IsoExport", "Import LOIN XML")
    path, _ = QFileDialog.getOpenFileName(
        widget.window(), title, "", constants.LOIN_FILETYPE
    )
    if not path:
        return
    try:
        Loin.import_from_xml(path)
    except Exception as exc:
        QMessageBox.critical(widget.window(), title, str(exc))


def _export_loin(widget: ui.Widget, iso_export: Type[tool.IsoExport]) -> None:
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    from bsdd_gui.tool.loin import Loin

    title = QCoreApplication.translate("IsoExport", "Export LOIN XML")
    path, _ = QFileDialog.getSaveFileName(
        widget.window(), title, "", constants.LOIN_FILETYPE
    )
    if not path:
        return
    try:
        count = Loin.export_to_xml(path)
        QMessageBox.information(
            widget.window(),
            title,
            QCoreApplication.translate("IsoExport", "{} specification(s) exported.").format(count),
        )
    except Exception as exc:
        QMessageBox.warning(widget.window(), title, str(exc))


def register_fields(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    pass


def register_validators(widget: ui.Widget, iso_epxort: Type[tool.IsoExport], util: Type[tool.Util]):
    pass



def connect_widget(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    iso_export.connect_widget_signals(widget)

def export_settings(
    widget: ui.Widget,
    iso_export: Type[tool.IsoExport],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    # Create Dict
    class_tree = widget.property_picker.tv_classes
    property_tree = widget.property_picker.tv_properties
    class_dict: dict[str, bool] = pp_class_view.get_check_dict(class_tree)
    property_dict: PsetDict = pp_property_view.get_check_dict(property_tree)
    settings_dict: SettingsDict = iso_export.get_settings(widget)
    full_dict: SettingsDict = {
        "class_settings": class_dict,
        "property_settings": property_dict,
        "settings": settings_dict,
    }

    # Set Path
    text = QCoreApplication.translate("IsoExport", "Export ISO 23386 settings")
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    new_path = popups.get_save_path(constants.SETTINGS_FILETYPE, widget.window(), old_path, text)
    if not new_path:
        return
    appdata.set_path(constants.APPDATA_OPTION, new_path)

    # Write Json
    with open(new_path, "w") as file:
        json.dump(full_dict, file)


def import_settings(
    widget: ui.Widget,
    iso_export: Type[tool.IsoExport],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    # Handle Path
    old_path = appdata.get_path(constants.APPDATA_OPTION)
    text = QCoreApplication.translate("IsoExport", "Import ISO23386 settings")
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

    # Fill Fields and Checkstates
    class_tree = widget.property_picker.tv_classes
    property_tree = widget.property_picker.tv_properties
    pp_class_view.set_check_dict(class_dict, class_tree)
    pp_property_view.set_check_dict(property_dict, property_tree)
    iso_export.set_settings(widget, settings_dict)
    pass

def export(    widget: ui.Widget,
    iso_export: Type[tool.IsoExport],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
    util:Type[tool.Util],
    project:type[tool.Project]):

    fmt = iso_export.get_export_format(widget)
    out_path = widget.fw_output.get_path()

    if fmt == constants.FORMAT_LOIN:
        iso_export.sync_to_model(widget, widget.bsdd_data)
        title = QCoreApplication.translate("IsoExport", "Export ISO 7817-3 (LOIN)")
        waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(title)
        waiting_widget.set_title("Serialise LOIN")

        def loin_done(count: int):
            stop_waiting_widget(waiting_worker)
            t = QCoreApplication.translate("IsoExport", "Export Done!")
            text_title = QCoreApplication.translate(
                "IsoExport", "ISO 7817-3 LOIN Export Done!"
            )
            text = QCoreApplication.translate(
                "IsoExport", "{} specification(s) exported!"
            ).format(count)
            QTimer.singleShot(0, widget, lambda: popups.create_info_popup(text, t, text_title, parent=widget))

        worker, thread = iso_export.create_loin_build_thread(out_path)
        worker.finished.connect(loin_done)
        worker.error.connect(lambda: stop_waiting_widget(waiting_worker))
        thread.start()
        return

    # Default / ISO 23386 path (existing behaviour).
    iso_export.sync_to_model(widget, widget.bsdd_data)
    title = QCoreApplication.translate("IsoExport", "Export ISO23386")
    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(title)
    waiting_widget.set_title("Load Data")

    bsdd_dict = project.get()
    class_settings = pp_class_view.build_full_check_dict(widget.property_picker.tv_classes,bsdd_dict)
    property_settings = pp_property_view.build_full_check_dict(widget.property_picker.tv_properties,bsdd_dict)
    base_settings = iso_export.get_settings(widget)

    def export_done(class_count:int):
        stop_waiting_widget(waiting_worker)
        t = QCoreApplication.translate("IsoExport","Export Done!")
        text_title = QCoreApplication.translate("IsoExport","ISO23386 Export Done!")
        text = QCoreApplication.translate("IsoExport","{} classes exported!").format(class_count)
        QTimer.singleShot(0, widget,  lambda: popups.create_info_popup(text,t,text_title,parent=widget))

    build_worker, build_thread = iso_export.create_build_thread(bsdd_dict,class_settings,property_settings,out_path)

    build_worker.finished.connect(export_done )
    build_worker.error.connect(lambda: stop_waiting_widget(waiting_worker))

    build_thread.start()

    


