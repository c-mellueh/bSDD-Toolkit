from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import graph_view_widget as core
from PySide6.QtWidgets import QWidget, QLineEdit
from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer import tool as gv_tool

if TYPE_CHECKING:
    from . import ui


def activate():
    core.connect_signals(
        gv_tool.GraphViewWidget,
        tool.RelationshipEditorWidget,
        tool.ClassPropertyTableView,
        tool.PropertySetTableView,
        tool.Project,
    )
    core.connect_to_main_window(gv_tool.GraphViewWidget, tool.MainWindowWidget)
    # w = core.create_widget(
    #     tool.MainWindowWidget.get(), gv_tool.GraphViewWidget, tool.MainWindowWidget, tool.Project
    # )
    # w.hide()


def deactivate():
    core.remove_main_menu_actions(gv_tool.GraphViewWidget, tool.MainWindowWidget)


def retranslate_ui():
    core.retranslate_ui(gv_tool.GraphViewWidget, tool.MainWindowWidget)


def on_new_project():
    pass
    # core.popuplate_widget(gv_tool.GraphViewWidget, tool.Project)


def widget_created(widget):
    core.register_widget(widget, gv_tool.GraphViewWidget)
    core.connect_widget(widget, gv_tool.GraphViewWidget)
    core.add_icons(widget)


def create_widget(parent: QWidget | None = None):
    core.create_widget(parent, gv_tool.GraphViewWidget, tool.MainWindowWidget, tool.Project)


def handle_drop_event(event, view: ui.GraphView):
    core.handle_drop_event(
        event,
        view,
        gv_tool.GraphViewWidget,
        tool.ClassTreeView,
        tool.PropertyTableWidget,
        tool.Project,
        tool.IfcHelper,
    )


def load_bsdd():
    core.popuplate_widget(gv_tool.GraphViewWidget, tool.Project, tool.IfcHelper)


def node_double_clicked(node):
    core.node_double_clicked(
        node, tool.PropertyTableWidget, tool.ClassTreeView, tool.MainWindowWidget
    )


def create_relation(start_node, end_node, relation_type):
    core.create_relation(start_node, end_node, relation_type, gv_tool.GraphViewWidget, tool.Project)


def delete_selection():
    core.delete_selection(gv_tool.GraphViewWidget, tool.Project)


def export_requested():
    core.export_graph(gv_tool.GraphViewWidget, tool.Popups, tool.Appdata)


def import_requested():
    core.import_graph(
        gv_tool.GraphViewWidget, tool.Project, tool.Popups, tool.Appdata, tool.IfcHelper
    )


def recalculate_edges():
    core.recalculate_edges(gv_tool.GraphViewWidget, tool.Project)


def buchheim():
    core.buchheim(gv_tool.GraphViewWidget, tool.Project)


def add_node_by_lineinput(window: ui.GraphWindow):
    core.add_node_by_lineinput(window, gv_tool.GraphViewWidget, tool.Project, tool.IfcHelper)


def enter_window(window: ui.GraphWindow):
    core.enter_window(window, gv_tool.GraphViewWidget, tool.Project)
