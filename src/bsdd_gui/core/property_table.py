from __future__ import annotations
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING, Type
from bsdd_gui.module.property_table import ui

if TYPE_CHECKING:
    from bsdd_gui import tool


def create_main_menu_actions(
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
    project: Type[tool.Project],
) -> None:
    action = main_window.add_action(
        "menuEdit",
        "bSDD Properties",
        lambda: property_table.request_widget(None, main_window.get()),
    )
    property_table.set_action(main_window.get(), "open_window", action)

    property_table.connect_internal_signals()


def retranslate_ui(
    property_table: Type[tool.PropertyTable],
    main_window: Type[tool.MainWindow],
    util: Type[tool.Util],
):
    """Retranslates the UI elements of dictionary Editor. and the Actions."""
    action = property_table.get_action(main_window.get(), "open_window")
    text = QCoreApplication.translate("PropertyTable", "bSDD Properties")
    action.setText(text)
    title = util.get_window_title(QCoreApplication.translate("PropertyTable", "bSDD Properties"))
    for widget in property_table.get_widgets():
        widget.setWindowTitle(title)


def create_widget(parent: QWidget, property_table: Type[tool.PropertyTable]):
    widget = property_table.create_widget()
    widget.show()


def register_widget(widget: ui.PropertyWidget, property_table: Type[tool.PropertyTable]):
    property_table.register_widget(widget)
    property_table.connect_widget_to_internal_signals(widget)

    # dictionary_editor.fill_dictionary_widget(widget)
    # dictionary_editor.color_required_fields(widget)


def unregister_widget(
    widget: ui.PropertyWidget,
    property_table: Type[tool.PropertyTable],
):
    property_table.unregister_widget(widget)
