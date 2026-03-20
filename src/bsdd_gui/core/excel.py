from __future__ import annotations
from PySide6.QtCore import QCoreApplication
from typing import TYPE_CHECKING, Type
import qtawesome as qta
if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.excel import ui


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
