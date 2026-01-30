from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.module.group_of_properties import ui


def connect_to_main_window(
    group_of_properties: Type[tool.GroupOfProperties],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing

    action = main_window.add_action(
        None,
        "GRoups of Properties",
        lambda: group_of_properties.request_widget(project.get(), main_window.get()),
    )
    group_of_properties.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    group_of_properties: Type[tool.GroupOfProperties], main_window: Type[tool.MainWindowWidget]
):
    action = group_of_properties.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GroupsOfProperties", "Groups of Properties"))


def connect_signals(widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.connect_internal_signals()


def create_widget(data, parent, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.show_widget(data, parent)


def register_widget(widget: ui.GopWidget, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.register_widget(widget)


def connect_widget(widget: ui.GopWidget, widget_tool: Type[tool.GroupOfProperties]):
    widget_tool.connect_widget_signals(widget)
