from __future__ import annotations
from PySide6.QtCore import QCoreApplication,QTimer
from typing import TYPE_CHECKING, Type
import qtawesome as qta
from bsdd_gui.module.iso_export import constants
from bsdd_gui.presets.ui_presets.waiting import stop_waiting_widget


if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.iso_export import ui

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


def register_widget(widget: ui.Widget, iso_export: Type[tool.IsoExport],property_picker:Type[tool.PropertyPicker]):
    iso_export.register_widget(widget)
    widget.fw_output.file_format = constants.ISO_FILETYPE
    widget.fw_output.section = "paths"
    widget.fw_output.option = "iso_23386"
    widget.fw_output.title = "get ISO23386-Export Path"

    widget.pb_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
    widget.pb_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
    widget.fw_output.load_path()


def register_fields(widget: ui.Widget, iso_export: Type[tool.IsoExport]):
    pass


def register_validators(widget: ui.Widget, iso_epxort: Type[tool.IsoExport], util: Type[tool.Util]):
    pass



def connect_widget(widget: ui.Widget, iso_export: Type[tool.IsoExport],property_picker:Type[tool.PropertyPicker]):
    widget.pb_import.clicked.connect(lambda _=False, w=widget: property_picker.request_xml_import(w))
    widget.pb_export.clicked.connect(lambda _=False, w=widget: property_picker.request_xml_export(w))
    iso_export.connect_widget_signals(widget)


def export( widget: ui.Widget,
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

    


