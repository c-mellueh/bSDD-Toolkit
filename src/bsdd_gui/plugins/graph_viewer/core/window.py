from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QCoreApplication, Qt

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.window import ui


def connect_to_main_window(
    window: Type[gv_tool.Window],
    main_window: Type[tool.MainWindowWidget],
    project: Type[tool.Project],
):
    # Action uses the WidgetTool request to allow trigger routing
    action = main_window.add_action(
        None, "Graph Viewer", lambda: window.request_widget(project.get(), main_window.get())
    )
    window.set_action(main_window.get(), "open_window", action)


def connect_signals(window: Type[gv_tool.Window]):
    window.connect_internal_signals()


def retranslate_ui(window: Type[gv_tool.Window], main_window: Type[tool.MainWindowWidget]):
    action = window.get_action(main_window.get(), "open_window")
    action.setText(QCoreApplication.translate("GraphView", "Graph Viewer"))


def create_widget(data, parent, window: Type[gv_tool.Window], scene_view: Type[gv_tool.SceneView]):
    widget = window.show_widget(data, parent)
    scene_view.reposition_help_overlay(widget.view)


def register_widget(widget: ui.GraphWidget, window: gv_tool.Window):
    window.register_widget(widget)


def connect_widget(widget: ui.GraphWidget, window: gv_tool.Window, util: Type[tool.Util]):
    window.connect_widget_signals(widget)
    util.add_shortcut(
        Qt.Key.Key_Space,
        widget,
        lambda w=widget: window.request_toggle_running(w),
        Qt.ShortcutContext.WidgetWithChildrenShortcut,
    )
    util.add_shortcut(
        Qt.Key.Key_Delete,
        widget,
        lambda w=widget: window.request_delete_selection(w),
        Qt.ShortcutContext.WidgetWithChildrenShortcut,
    )
