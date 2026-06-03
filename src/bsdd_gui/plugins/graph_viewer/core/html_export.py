from __future__ import annotations


from typing import TYPE_CHECKING
from bsdd_gui.plugins.graph_viewer.module.html_export import constants
from bsdd_json.utils import class_utils as cl_utils
from PySide6.QtCore import QCoreApplication, QPointF

if TYPE_CHECKING:
    import bsdd_gui.plugins.graph_viewer.tool as gv_tool
    from bsdd_gui import tool
    from bsdd_json import BsddClass, BsddDictionary


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

    # Bundle the current scene into a single tab and render the page.
    tab = html_export.generate_graph_tab(
        "", nodes, edges, bsdd_dictionary, orthogonal, arrow_length
    )
    page_title, heading_suffix = html_export.generate_title(bsdd_dictionary)
    html_content = html_export.generate_tabbed_html(page_title, heading_suffix, [tab])
    html_export.write_html(html_content, path, window)


def _collect_subtree(root: BsddClass, bsdd_dictionary: BsddDictionary) -> list[BsddClass]:
    """Return the root class followed by all of its descendant classes."""
    result: list[BsddClass] = []
    seen: set[str] = set()
    stack = [root]
    while stack:
        bsdd_class = stack.pop()
        if bsdd_class.Code in seen:
            continue
        seen.add(bsdd_class.Code)
        result.append(bsdd_class)
        stack.extend(cl_utils.get_children(bsdd_class, bsdd_dictionary))
    return result


def export_html_tabs(
    window: type[gv_tool.Window],
    node: type[gv_tool.Node],
    edge: type[gv_tool.Edge],
    scene_view: type[gv_tool.SceneView],
    buchheim: type[gv_tool.Buchheim],
    project: type[tool.Project],
    popups: type[tool.Popups],
    appdata: type[tool.Appdata],
    html_export: type[gv_tool.HTMLExport],
):
    """Export one HTML page with a tab per root class.

    For each root class its whole subtree is laid out automatically (clear scene →
    insert subtree → recalculate edges → tree layout), captured as a tab, and the
    scene is reused for the next root. This replaces the manual per-root workflow.
    """
    from bsdd_gui.plugins.graph_viewer.module.edge import constants as ec

    bsdd_dictionary = project.get()
    roots = [c for c in cl_utils.get_root_classes(bsdd_dictionary) if c.ClassType == "Class"]
    if not roots:
        # Nothing to lay out automatically — fall back to the current scene export.
        export_html_graph(window, node, edge, project, popups, appdata, html_export)
        return

    last_path = appdata.get_path(constants.HTML_PATH_NAME) or "graph_view.html"
    text = QCoreApplication.translate("GraphViewer", "Export Graph as HTML (one tab per root class)")
    path = popups.get_save_path(constants.HTML_FILETYPE, window.get_widget(), last_path, text)
    if not path:
        return
    appdata.set_path(constants.HTML_PATH_NAME, path)

    orthogonal = edge.is_orthogonal_mode()
    arrow_length = edge.get_properties().arrow_length

    # The tree layout follows parent/child edges; force that relation active meanwhile.
    previous_active_edge = edge.get_active_edge()
    edge.set_active_edge(ec.PARENT_CLASS)

    tabs: list[dict] = []
    try:
        for root in roots:
            scene_view.request_clear_scene()
            classes = _collect_subtree(root, bsdd_dictionary)
            scene_view.request_classes_insert(classes, QPointF(0.0, 0.0))
            scene_view.request_recalculate_edges()

            # Size each box to its label *before* layout: buchheim spaces nodes by their
            # width, and unpainted nodes would otherwise report the default width and
            # squash the whole tree.
            html_export.ensure_node_sizes(node.get_nodes())
            buchheim.request_tree_creation()

            nodes = node.get_visible_nodes()
            edges = edge.get_visible_edges(nodes)
            if not nodes:
                continue
            tabs.append(
                html_export.generate_graph_tab(
                    root.Name or root.Code,
                    nodes,
                    edges,
                    bsdd_dictionary,
                    orthogonal,
                    arrow_length,
                )
            )
    finally:
        scene_view.request_clear_scene()
        edge.set_active_edge(previous_active_edge)

    page_title, heading_suffix = html_export.generate_title(bsdd_dictionary)
    if tabs:
        html_content = html_export.generate_tabbed_html(page_title, heading_suffix, tabs)
    else:
        html_content = html_export.generate_empty_html()
    html_export.write_html(html_content, path, window)
