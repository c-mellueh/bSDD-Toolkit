from __future__ import annotations
from PySide6.QtCore import QCoreApplication,QTimer
from typing import TYPE_CHECKING, Type
import qtawesome as qta
from bsdd_gui.module.excel import constants
import json
from bsdd_json.utils import class_utils
from bsdd_gui.presets.ui_presets.waiting import stop_waiting_widget


if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.excel import ui
    from bsdd_gui.tool.property_picker import PsetDict
    from bsdd_gui.tool.excel import SettingsDict
    from bsdd_json import BsddClass

def connect_to_main_window(
    excel: Type[tool.Excel],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing 
    action = main_window.add_action(
        "menuFile",
        "Export Excel",
        lambda: excel.request_widget(
            project.get(),
            main_window.get(),
        ),
        qta.icon("mdi6.file-excel"),

    )
    excel.set_action(main_window.get(), "open_window", action)


def connect_signals(excel: Type[tool.Excel]):
    excel.connect_internal_signals()


def retranslate_ui(excel: Type[tool.Excel],main_window:type[tool.MainWindowWidget]):
    action = excel.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("Excel", "Export Excel"))



def create_widget(data, parent, excel: Type[tool.Excel]):
    excel.show_widget(data, parent)


def register_widget(widget: ui.Widget, excel: Type[tool.Excel]):
    excel.register_widget(widget)
    widget.fw_output.file_format = constants.EXCEL_FILETYPE
    widget.fw_output.section = "paths"
    widget.fw_output.option = "excel"
    widget.fw_output.title = "get Excel-Export Path"

    widget.pb_import.setIcon(qta.icon("mdi6.tray-arrow-up"))
    widget.pb_export.setIcon(qta.icon("mdi6.tray-arrow-down"))
    widget.fw_output.load_path()
    widget.settings_widget.setVisible(False)

def register_fields(widget: ui.Widget, excel: Type[tool.Excel]):
    pass
    #excel.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget: ui.Widget, excel: Type[tool.Excel], util: Type[tool.Util]):
    pass
    # excel.add_validator(
    #     widget,
    #     widget.le_code,
    #     lambda v, w,: excel.is_code_valid(v, w),
    #     lambda w, v: util.set_invalid(w, not v),
    # )


def connect_widget(widget: ui.Widget, excel: Type[tool.Excel]):
    excel.connect_widget_signals(widget)

def export_settings(
    widget: ui.Widget,
    widget_tool: Type[tool.Excel],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    return


def import_settings(
    widget: ui.Widget,
    widget_tool: Type[tool.Excel],
    pp_class_view: Type[tool.PPClassView],
    pp_property_view: Type[tool.PPPropertyView],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
):
    return

def export(    widget: ui.Widget,
    excel: Type[tool.Excel],
    appdata: Type[tool.Appdata],
    popups: Type[tool.Popups],
    util:Type[tool.Util],
    project:type[tool.Project],
    property_picker:Type[tool.PropertyPicker],):
    
    excel.sync_to_model(widget, widget.bsdd_data)
    title = QCoreApplication.translate("Excel", "Export Excel")
    waiting_worker, waiting_thread, waiting_widget = util.create_waiting_widget(title)
    waiting_widget.set_title("Load Data")
    bsdd_dict = project.get()

    specs = property_picker.select_specs_dialog(widget)
    if not specs:
        return
    checked_classes = property_picker.get_checked_classes(specs,bsdd_dict)
    checked_properties = property_picker.get_checked_properties(specs,bsdd_dict)
    base_settings = excel.get_settings(widget)
    out_path = widget.fw_output.get_path()

    def export_done(classes:list[BsddClass]):
        stop_waiting_widget(waiting_worker)
        title = QCoreApplication.translate("Excel","Export Done!")
        text_title = QCoreApplication.translate("Excel","Excel Export Done!")
        text = QCoreApplication.translate("Excel","{} classes exported!").format(len(classes))
        QTimer.singleShot(0, widget,  lambda: popups.create_info_popup(text,title,text_title,parent=widget))
        
    

    build_worker, build_thread = excel.create_build_thread(bsdd_dict,checked_classes,checked_properties,out_path)

    build_worker.finished.connect(export_done )
    build_worker.error.connect(lambda: stop_waiting_widget(waiting_worker))

    build_thread.start()

    


