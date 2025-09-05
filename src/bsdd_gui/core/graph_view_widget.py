from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from bsdd_gui import tool


def connect_signals(graph_view: Type[tool.GraphViewWidget]):
    graph_view.connect_internal_signals()


def connect_to_main_window(
    graph_view: Type[tool.GraphViewWidget],
    main_window: Type[tool.MainWindowWidget],
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action("menuData", "Graph View", lambda: graph_view.request_widget())
    graph_view.set_action(main_window.get(), "open_window", action)


def retranslate_ui(
    graph_view: Type[tool.GraphViewWidget],
    main_window: Type[tool.MainWindowWidget],
):
    action = graph_view.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GraphView", "Graph View"))


def create_widget(
    parent: QWidget | None,
    graph_view: Type[tool.GraphViewWidget],
    main_window: Type[tool.MainWindowWidget],
):
    # Default parent to the main window if not provided
    if parent is None:
        parent = main_window.get()
    w = graph_view.create_widget(parent)
    # Show as independent window
    w.show()
    w.activateWindow()
    w.raise_()
    return w


def register_widget(widget, graph_view: Type[tool.GraphViewWidget]):
    graph_view.register_widget(widget)


def connect_widget(widget, graph_view: Type[tool.GraphViewWidget]):
    graph_view.connect_widget_signals(widget)
