from __future__ import annotations
from bsdd_gui.plugins.graph_viewer.core import html_export as core
from bsdd_gui.plugins.graph_viewer import tool as gv_tool
from bsdd_gui import tool


def activate():
    core.connect_signals(gv_tool.HTMLExport)


def deactivate():
    core.disconnect_signals(gv_tool.HTMLExport)


def retranslate_ui():
    pass


def on_new_project():
    pass


def export_html():
    core.export_html_graph(
        gv_tool.Window,
        gv_tool.Node,
        gv_tool.Edge,
        tool.Project,
        tool.Popups,
        tool.Appdata,
        gv_tool.HTMLExport,
    )
