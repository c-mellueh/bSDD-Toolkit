from __future__ import annotations
from PySide6.QtCore import QCoreApplication, QTimer
from typing import TYPE_CHECKING, Type
import qtawesome as qta
from bsdd_gui.module.revit_export import constants
from bsdd_gui.presets.ui_presets.waiting import stop_waiting_widget


if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.revit_export import ui
    from bsdd_json import BsddClass


def connect_to_main_window(
    revit_export: Type[tool.RevitExport],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action(
        "menuFile",
        "Export Revit",
        lambda: revit_export.request_widget(
            project.get(),
            main_window.get(),
        ),
        qta.icon("mdi6.file"),
    )
    revit_export.set_action(main_window.get(), "open_window", action)


def connect_signals(revit_export: Type[tool.RevitExport]):
    revit_export.connect_internal_signals()


def retranslate_ui(revit_export: Type[tool.RevitExport], main_window: type[tool.MainWindowWidget]):
    action = revit_export.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("RevitExport", "Export Revit"))
    for wid in revit_export.get_widgets():
        wid:ui.Widget
        wid.setWindowTitle(wid.tr("Export to Revit"))

def create_widget(data, parent, revit_export: Type[tool.RevitExport]):
    revit_export.show_widget(data, parent)


def register_widget(widget: ui.Widget, revit_export: Type[tool.RevitExport]):
    revit_export.register_widget(widget)
    widget.fw_output.file_format = constants.SHARED_PARAMETERS_FILETYPE
    widget.fw_output.section = "paths"
    widget.fw_output.option = "RevitExport"
    widget.fw_output.title = "get Revit-Export Path"

    widget.pb_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
    widget.pb_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
    widget.fw_output.load_path()
    widget.settings_widget.setVisible(False)


def register_fields(widget: ui.Widget, revit_export: Type[tool.RevitExport]):
    pass
    # revit_export.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget: ui.Widget, revit_export: Type[tool.RevitExport], util: Type[tool.Util]):
    pass
    # revit_export.add_validator(
    #     widget,
    #     widget.le_code,
    #     lambda v, w,: revit_export.is_code_valid(v, w),
    #     lambda w, v: util.set_invalid(w, not v),
    # )


def connect_widget(widget: ui.Widget, revit_export: Type[tool.RevitExport]):
    revit_export.connect_widget_signals(widget)


def export_settings(
    widget: ui.Widget,
    widget_tool: Type[tool.RevitExport],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    return


def import_settings(
    widget: ui.Widget,
    widget_tool: Type[tool.RevitExport],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    return


def export(
    widget: ui.Widget,
    revit_export: Type[tool.RevitExport],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
    util: Type[tool.Util],
    project: type[tool.Project],
    loin: Type[tool.Loin],
):

    revit_export.sync_to_model(widget, widget.bsdd_data)
    title = QCoreApplication.translate("RevitExport", "Export Revit")
    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(title)
    waiting_widget.set_title("Load Data")
    bsdd_dict = project.get()

    specs = loin.select_specs_dialog(widget)
    if not specs:
        return
    checked_classes = loin.get_checked_classes(specs, bsdd_dict)
    checked_properties = loin.get_checked_properties(specs, bsdd_dict)
    out_path = widget.fw_output.get_path()

    def export_done(classes: list[BsddClass]):
        stop_waiting_widget(waiting_worker)
        title = QCoreApplication.translate("RevitExport", "Export Done!")
        text_title = QCoreApplication.translate("RevitExport", "Revit Export Done!")
        text = QCoreApplication.translate("RevitExport", "{} classes exported!").format(len(classes))
        QTimer.singleShot(
            0, widget, lambda: popups.create_info_popup(text, title, text_title, parent=widget)
        )

    build_worker, build_thread = revit_export.create_build_thread(
        bsdd_dict, checked_classes, checked_properties, out_path
    )

    build_worker.finished.connect(export_done)
    build_worker.error.connect(lambda: stop_waiting_widget(waiting_worker))

    build_thread.start()
