from __future__ import annotations


from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer.module.html_export import constants
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
    """Generate HTML Export of all Nodes that are currently contained in the Scene."""
    # reqest Path
    last_path = appdata.get_path(constants.HTML_PATH_NAME) or "graph_view.html"
    text = QCoreApplication.translate("GraphViewer", "Export Graph as HTML")
    path = popups.get_save_path(constants.HTML_FILETYPE, window.get_widget(), last_path, text)
    if not path:
        return
    appdata.set_path(constants.HTML_PATH_NAME, path)

    # Get data from Scene
    bsdd_dictionary = project.get()
    orthogonal = edge.is_orthogonal_mode()
    arrow_length = edge.get_properties().arrow_length
    nodes = node.get_visible_nodes()
    edges = edge.get_visible_edges(nodes)

    # If Empty
    if not nodes:
        html_content = html_export.generate_empty_html()
        html_export.write_html(html_content, path, window)
        return

    # Generate HTML Parts
    svg_w, svg_h, offset_x, offset_y = html_export.compute_bounding_box(nodes)
    defs_parts, edge_parts = html_export.generate_edge_parts(
        edges,
        offset_x,
        offset_y,
        orthogonal,
        arrow_length,
    )
    node_parts = html_export.generate_node_parts(nodes, offset_x, offset_y, bsdd_dictionary)
    node_legend_html = html_export.generate_node_legend(nodes)
    edge_legend_html = html_export.generate_edge_legend(edges)

    page_title, heading_suffix = html_export.generate_title(bsdd_dictionary)

    # Generate HTML Content
    html_content = html_export.generate_html(
        page_title,
        heading_suffix,
        svg_w,
        svg_h,
        defs_parts,
        edge_parts,
        node_parts,
        node_legend_html,
        edge_legend_html,
    )

    # Write to File
    html_export.write_html(html_content, path, window)
