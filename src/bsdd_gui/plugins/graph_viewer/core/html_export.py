from __future__ import annotations


from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer.module.html_export import constants
import logging
from PySide6.QtCore import QCoreApplication

if TYPE_CHECKING:
    import bsdd_gui.plugins.graph_viewer.tool as gv_tool
    from bsdd_gui import tool


def connect_signals(
    html_export: type[gv_tool.HTMLExport],
):
    html_export.connect_internal_signals()


def disconnect_signals(html_export: type[gv_tool.HTMLExport]):
    html_export.disconnect_internal_signals()
    html_export.disconnect_external_signals()


def export_html_graph(
    window: type[gv_tool.Window],
    node: type[gv_tool.Node],
    edge: type[gv_tool.Edge],
    project: type[tool.Project],
    popups: type[tool.Popups],
    appdata: type[tool.Appdata],
    html_export: type[gv_tool.HTMLExport],
):
    last_path = appdata.get_path(constants.HTML_PATH_NAME) or "graph_view.html"
    text = QCoreApplication.translate("GraphViewer", "Export Graph as HTML")
    path = popups.get_save_path(constants.HTML_FILETYPE, window.get_widget(), last_path, text)
    if not path:
        return
    appdata.set_path(constants.HTML_PATH_NAME, path)

    bsdd_dictionary = project.get()
    nodes = node.get_nodes()
    edges = edge.get_edges()
    edge_filters = edge.get_filters()
    node_filters = node.get_filters()

    orthogonal = edge.is_orthogonal_mode()
    arrow_length = edge.get_properties().arrow_length
    html_content = html_export.generate_html(
        nodes, edges, bsdd_dictionary, edge_filters, node_filters, orthogonal, arrow_length
    )
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        try:
            text = QCoreApplication.translate("GraphViewer", "HTML exported: ") + str(path)
            window.set_status(text)
        except Exception:
            pass
    except Exception as e:
        logging.exception("Failed to export HTML: %s", e)
