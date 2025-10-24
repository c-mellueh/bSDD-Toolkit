from __future__ import annotations
from PySide6.QtCore import QCoreApplication
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.ids_exporter import ui


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
    action.setText(QCoreApplication.translate("GraphView", "Graph View"))


def connect_signals(widget_tool: Type[tool.IdsExporter]):
    widget_tool.connect_internal_signals()


def create_widget(data, parent, widget_tool: Type[tool.IdsExporter]):
    widget:ui.IdsWidget = widget_tool.show_widget(data, parent)


def create_dialog(data: object, parent, dialog_tool: Type[tool.IdsExporter]):
    dialog = dialog_tool.create_dialog(data, parent)
    text = QCoreApplication.translate("Preset", "Example Title")
    dialog.setWindowTitle(text)
    if dialog.exec():
        dialog_tool.sync_to_model(dialog._widget, data)
        dialog_tool.signals.dialog_accepted.emit(dialog)
    else:
        dialog_tool.signals.dialog_declined.emit(dialog)


def register_widget(widget: ui.IdsWidget, widget_tool: Type[tool.IdsExporter]):
    widget_tool.register_widget(widget)


def register_fields(widget: ui.IdsWidget, widget_Tool: Type[tool.IdsExporter]):
    widget_Tool.register_basic_field(widget, widget.le_name, "Name")


def register_validators(widget, widget_tool: Type[tool.IdsExporter], util: Type[tool.Util]):
    widget_tool.add_validator(
        widget,
        widget.le_code,
        lambda v, w,: widget_tool.is_code_valid(v, w),
        lambda w, v: util.set_invalid(w, not v),
    )


def connect_widget(widget: ui.IdsWidget, widget_tool: Type[tool.IdsExporter]):
    widget_tool.connect_widget_signals(widget)
