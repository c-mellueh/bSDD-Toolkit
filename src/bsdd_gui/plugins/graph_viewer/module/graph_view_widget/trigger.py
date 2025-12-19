from __future__ import annotations
import bsdd_gui
from bsdd_gui import tool
from bsdd_gui.plugins.graph_viewer.core import graph_view_widget as core
from PySide6.QtWidgets import QWidget, QLineEdit
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import ui


def connect():
    core.connect_signals(
        tool.GraphViewWidget,
        tool.RelationshipEditorWidget,
        tool.ClassPropertyTableView,
        tool.PropertySetTableView,
        tool.Project,
    )
    core.connect_to_main_window(tool.GraphViewWidget, tool.MainWindowWidget)
    w = core.create_widget(
        tool.MainWindowWidget.get(), tool.GraphViewWidget, tool.MainWindowWidget, tool.Project
    )
    w.hide()


def retranslate_ui():
    core.retranslate_ui(tool.GraphViewWidget, tool.MainWindowWidget)


def on_new_project():
    pass
    # core.popuplate_widget(tool.GraphViewWidget, tool.Project)


def widget_created(widget):
    core.register_widget(widget, tool.GraphViewWidget)
    core.connect_widget(widget, tool.GraphViewWidget)
    core.add_icons(widget)

def create_widget(parent: QWidget | None = None):
    core.create_widget(parent, tool.GraphViewWidget, tool.MainWindowWidget, tool.Project)


def handle_drop_event(event, view: ui.GraphView):
    core.handle_drop_event(
        event,
        view,
        tool.GraphViewWidget,
        tool.ClassTreeView,
        tool.PropertyTableWidget,
        tool.Project,
        tool.IfcHelper,
    )


def load_bsdd():
    core.popuplate_widget(tool.GraphViewWidget, tool.Project, tool.IfcHelper)


def node_double_clicked(node):
    core.node_double_clicked(
        node, tool.PropertyTableWidget, tool.ClassTreeView, tool.MainWindowWidget
    )


def create_relation(start_node, end_node, relation_type):
    core.create_relation(start_node, end_node, relation_type, tool.GraphViewWidget, tool.Project)


def delete_selection():
    core.delete_selection(tool.GraphViewWidget, tool.Project)


def export_requested():
    core.export_graph(tool.GraphViewWidget, tool.Popups, tool.Appdata)


def import_requested():
    core.import_graph(tool.GraphViewWidget, tool.Project, tool.Popups, tool.Appdata, tool.IfcHelper)


def recalculate_edges():
    core.recalculate_edges(tool.GraphViewWidget, tool.Project)


def buchheim():
    core.buchheim(tool.GraphViewWidget, tool.Project)


def add_node_by_lineinput(window: ui.GraphWindow):
    core.add_node_by_lineinput(window, tool.GraphViewWidget, tool.Project, tool.IfcHelper)


def enter_window(window: ui.GraphWindow):
    core.enter_window(window, tool.GraphViewWidget, tool.Project)
