from __future__ import annotations
from typing import TYPE_CHECKING
import html
import math
import logging
from PySide6.QtCore import Signal, QCoreApplication
import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.html_export import constants, trigger
from bsdd_gui.presets.tool_presets import PluginTool, PluginSignals
from bsdd_gui.plugins.graph_viewer.module.edge import constants as ec
from bsdd_gui.plugins.graph_viewer.module.node import constants as nc

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.html_export.prop import HTMLExportProperties
    from bsdd_json import BsddDictionary
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge
    from bsdd_gui.plugins.graph_viewer.tool import Window as WindowTool


class Signals(PluginSignals):
    export_requested = Signal()


class HTMLExport(PluginTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> HTMLExportProperties:
        return bsdd_gui.HTMLExportProperties

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.export_requested.connect(trigger.export_html)
        return super().connect_internal_signals()

    @classmethod
    def request_export(cls):
        cls.signals.export_requested.emit()

    @classmethod
    def _qcolor_to_css(cls, color) -> str:
        r, g, b, a = color.red(), color.green(), color.blue(), color.alpha()
        if a >= 254:
            return f"rgb({r},{g},{b})"
        return f"rgba({r},{g},{b},{a / 255:.2f})"

    @classmethod
    def _dash_array(cls, pen_style) -> str:
        from PySide6.QtCore import Qt

        if pen_style == Qt.PenStyle.DotLine:
            return "3,5"
        if pen_style == Qt.PenStyle.DashLine:
            return "10,5"
        if pen_style == Qt.PenStyle.DashDotLine:
            return "10,5,3,5"
        if pen_style == Qt.PenStyle.DashDotDotLine:
            return "10,5,3,5,3,5"
        return ""

    # ---------------------------------------------------------------------------
    # Geometry helpers – mirror of tool/edge.py anchor calculations
    # ---------------------------------------------------------------------------
    @classmethod
    def _straight_anchor(
        cls,
        cx: float,
        cy: float,
        w: float,
        h: float,
        node_shape: str,
        toward_x: float,
        toward_y: float,
    ) -> tuple[float, float]:
        """Replicate Edge._calculate_anchor_on_node (straight mode).

        Returns the point on the node boundary closest to *toward* along the
        direction from the node centre.
        """
        from bsdd_gui.plugins.graph_viewer.module.node import constants as nc

        dx, dy = toward_x - cx, toward_y - cy
        length = math.hypot(dx, dy)
        if length < 1e-6:
            return cx, cy
        nx, ny = dx / length, dy / length
        hw, hh = max(w, 30.0) / 2.0, max(h, 16.0) / 2.0
        if node_shape == nc.SHAPE_STYPE_ELLIPSE:
            denom = (nx / max(hw, 1e-6)) ** 2 + (ny / max(hh, 1e-6)) ** 2
            t = 1.0 / math.sqrt(max(denom, 1e-9))
        else:
            tx = hw / abs(nx) if abs(nx) > 1e-6 else float("inf")
            ty = hh / abs(ny) if abs(ny) > 1e-6 else float("inf")
            t = min(tx, ty)
        return cx + nx * t, cy + ny * t

    @classmethod
    def _ortho_anchor(
        cls,
        cx: float,
        cy: float,
        w: float,
        h: float,
        toward_x: float,
        toward_y: float,
        hor_mode: bool,
    ) -> tuple[float, float]:
        """Replicate Edge._ortho_start.

        Returns the node-boundary exit point for orthogonal routing.
        """
        dx, dy = toward_x - cx, toward_y - cy
        hw, hh = max(w, 30.0) / 2.0, max(h, 16.0) / 2.0
        if hor_mode:
            dw = math.copysign(hw, dx) if abs(dx) > 1e-6 else 0.0
            return cx + dw, cy
        else:
            dh = math.copysign(hh, dy) if abs(dy) > 1e-6 else 0.0
            return cx, cy + dh

    @classmethod
    def _ortho_waypoints(
        cls,
        psx: float,
        psy: float,
        pex: float,
        pey: float,
        hor_mode: bool,
        arrow_length: float,
    ) -> list[tuple[float, float]]:
        """Replicate draw_ortho_line waypoints (including the final end-tip point).

        Returns an ordered list of (x, y) points from p_start to p_end_tip.
        """
        dx = pex - psx
        dy = pey - psy
        x_dir = math.copysign(1.0, dx) if abs(dx) > 1e-6 else 0.0
        y_dir = math.copysign(1.0, dy) if abs(dy) > 1e-6 else 0.0
        if hor_mode:
            x_height = pex - arrow_length * x_dir * 3
            p1 = (x_height, psy)
            p2 = (x_height, pey)
        else:
            y_height = pey - arrow_length * y_dir * 3
            p1 = (psx, y_height)
            p2 = (pex, y_height)
        return [(psx, psy), p1, p2, (pex, pey)]

    @classmethod
    def _edge_path_points(
        cls,
        sn: Node,
        en: Node,
        offset_x: float,
        offset_y: float,
        orthogonal: bool,
        arrow_length: float,
    ) -> list[tuple[float, float]] | None:
        """Return the ordered SVG path waypoints for a single edge."""
        scx = sn.pos().x() + offset_x
        scy = sn.pos().y() + offset_y
        ecx = en.pos().x() + offset_x
        ecy = en.pos().y() + offset_y

        if math.hypot(ecx - scx, ecy - scy) < 1e-6:
            return None

        if not orthogonal:
            psx, psy = cls._straight_anchor(scx, scy, sn._w, sn._h, sn.node_shape, ecx, ecy)
            pex, pey = cls._straight_anchor(ecx, ecy, en._w, en._h, en.node_shape, scx, scy)
            return [(psx, psy), (pex, pey)]

        # Orthogonal mode — match _ortho_mode_is_hor which checks the centre-to-centre delta
        hor_mode = abs(ecy - scy) < arrow_length * 3
        psx, psy = cls._ortho_anchor(scx, scy, sn._w, sn._h, ecx, ecy, hor_mode)
        pex, pey = cls._ortho_anchor(ecx, ecy, en._w, en._h, scx, scy, hor_mode)
        return cls._ortho_waypoints(psx, psy, pex, pey, hor_mode, arrow_length)

    # ---------------------------------------------------------------------------
    # Node helpers
    # ---------------------------------------------------------------------------
    @classmethod
    def _node_url(cls, node: Node, bsdd_dictionary: BsddDictionary | None) -> str | None:
        from bsdd_gui.plugins.graph_viewer.module.node import constants as nc
        from bsdd_json.utils import class_utils as cl_utils
        from bsdd_json.utils import property_utils as prop_utils

        try:
            if node.node_type in (nc.CLASS_NODE_TYPE, nc.GOP_NODE_TYPE):
                uri = cl_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
                return cls._use_latest_version(uri, bsdd_dictionary)
            if node.node_type == nc.EXTERNAL_CLASS_NODE_TYPE:
                return node.bsdd_data.OwnedUri
            if node.node_type == nc.PROPERTY_NODE_TYPE:
                uri = prop_utils.build_bsdd_uri(node.bsdd_data, bsdd_dictionary)
                return cls._use_latest_version(uri, bsdd_dictionary)
            if node.node_type in (nc.EXTERNAL_PROPERTY_NODE_TYPE, nc.IFC_NODE_TYPE):
                return node.bsdd_data.OwnedUri
        except Exception:
            pass
        return None

    @classmethod
    def _use_latest_version(
        cls, uri: str | None, bsdd_dictionary: BsddDictionary | None
    ) -> str | None:
        """Replace the dictionary version segment in an internal bSDD URI with ``latest``.

        bSDD resolves ``.../<org>/<dict>/latest/...`` to the most recent version, so the
        exported links keep working as the dictionary is republished.
        """
        if not uri or bsdd_dictionary is None:
            return uri
        version = bsdd_dictionary.DictionaryVersion
        if not version:
            return uri
        return uri.replace(f"/{version}/", "/latest/", 1)

    @classmethod
    def _node_shape_element(cls, node: Node, cx: float, cy: float) -> str:
        from bsdd_gui.plugins.graph_viewer.module.node import constants as nc

        w = max(node._w, 30.0)
        h = max(node._h, 16.0)
        x, y = cx - w / 2, cy - h / 2
        fill = cls._qcolor_to_css(node.color)
        stroke = constants.NODE_BORDER

        if node.node_shape == nc.SHAPE_STYPE_ELLIPSE:
            return (
                f'<ellipse class="node-shape" cx="{cx:.1f}" cy="{cy:.1f}" '
                f'rx="{w / 2:.1f}" ry="{h / 2:.1f}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="1.2"/>'
            )
        if node.node_shape == nc.SHAPE_STYLE_ROUNDED_RECT:
            return (
                f'<rect class="node-shape" x="{x:.1f}" y="{y:.1f}" '
                f'width="{w:.1f}" height="{h:.1f}" rx="6" ry="6" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="1.2"/>'
            )
        return (
            f'<rect class="node-shape" x="{x:.1f}" y="{y:.1f}" '
            f'width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.2"/>'
        )

    @classmethod
    def compute_bounding_box(cls, nodes: list[Node]):
        # Compute bounding box
        xs = [n.pos().x() for n in nodes]
        ys = [n.pos().y() for n in nodes]
        half_ws = [max(n._w, 30.0) / 2 for n in nodes]
        half_hs = [max(n._h, 16.0) / 2 for n in nodes]
        min_x = min(x - hw for x, hw in zip(xs, half_ws)) - constants.PADDING
        max_x = max(x + hw for x, hw in zip(xs, half_ws)) + constants.PADDING
        min_y = min(y - hh for y, hh in zip(ys, half_hs)) - constants.PADDING
        max_y = max(y + hh for y, hh in zip(ys, half_hs)) + constants.PADDING

        svg_w = max_x - min_x
        svg_h = max_y - min_y
        offset_x = -min_x
        offset_y = -min_y

        return svg_w, svg_h, offset_x, offset_y

    @classmethod
    def generate_arrowhead_defs(cls, edges: list[Edge]):
        # Arrow marker definitions — one per edge type that appears in the graph.
        # Using markerUnits="userSpaceOnUse" keeps the arrowhead a fixed pixel size
        # regardless of stroke width.
        used_edge_types = {e.edge_type for e in edges}
        marker_ids: dict[str, str] = {}
        defs_parts: list[str] = []
        for etype in used_edge_types:
            style = ec.EDGE_STYLE_MAP.get(etype, ec.EDGE_STYLE_DEFAULT)
            fill = cls._qcolor_to_css(style["color"])
            safe_id = f"arrow-{etype}"
            marker_ids[etype] = safe_id
            # Triangle: tip at (10,5), base at (0,0) and (0,10).
            # refX=10 → tip coincides with the path endpoint (on the node boundary).
            defs_parts.append(
                f'<marker id="{safe_id}" markerWidth="10" markerHeight="10" '
                f'refX="10" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0,0 L10,5 L0,10 Z" fill="{fill}"/>'
                f"</marker>"
            )
        return marker_ids, defs_parts

    @classmethod
    def generate_edge_parts(
        cls, edges: list[Edge], offset_x, offset_y, orthogonal, arrow_length
    ) -> list[str]:

        marker_ids, defs_parts = cls.generate_arrowhead_defs(edges)

        # Edge elements
        edge_parts: list[str] = []
        for edge in edges:
            pts = cls._edge_path_points(
                edge.start_node, edge.end_node, offset_x, offset_y, orthogonal, arrow_length
            )
            if pts is None:
                continue

            style = ec.EDGE_STYLE_MAP.get(edge.edge_type, ec.EDGE_STYLE_DEFAULT)
            color = cls._qcolor_to_css(style["color"])
            width = style.get("width", 1.5)
            dash = cls._dash_array(style.get("style"))
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            marker_attr = (
                f' marker-end="url(#{marker_ids[edge.edge_type]})"'
                if edge.edge_type in marker_ids
                else ""
            )

            # Build SVG path data: M first L rest...
            d = f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"
            for px, py in pts[1:]:
                d += f" L {px:.1f},{py:.1f}"

            edge_parts.append(
                f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
                f"{dash_attr}{marker_attr}/>"
            )
        return defs_parts, edge_parts

    @classmethod
    def generate_node_parts(
        cls, nodes: list[Node], offset_x: float, offset_y: float, bsdd_dictionary: BsddDictionary
    ) -> list[str]:

        # Node elements
        node_parts: list[str] = []
        for node in nodes:
            cx = node.pos().x() + offset_x
            cy = node.pos().y() + offset_y
            shape_el = cls._node_shape_element(node, cx, cy)
            label = html.escape(node.label or "")
            text_el = (
                f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
                f'dominant-baseline="middle" fill="{constants.TEXT_COLOR}" '
                f'font-size="12" font-family="sans-serif" pointer-events="none">{label}</text>'
            )

            # Class and Property nodes are selectable: a single click shows the node's
            # definition (and, for classes, its property table); a double click opens the
            # bSDD page (see inline script).
            select_id = cls._node_select_id(node)
            if select_id is not None:
                url = cls._node_url(node, bsdd_dictionary) if bsdd_dictionary else None
                href_attr = f' data-href="{html.escape(url)}"' if url else ""
                node_parts.append(
                    f'<g class="selectable" data-node-id="{html.escape(select_id)}"'
                    f"{href_attr}>{shape_el}{text_el}</g>"
                )
                continue

            inner = f"<g>{shape_el}{text_el}</g>"
            url = cls._node_url(node, bsdd_dictionary) if bsdd_dictionary else None
            if url:
                inner = (
                    f'<a href="{html.escape(url)}" target="_blank" '
                    f'xlink:href="{html.escape(url)}" style="cursor:pointer">{inner}</a>'
                )
            node_parts.append(inner)
        return node_parts

    @classmethod
    def _node_select_id(cls, node: Node) -> str | None:
        """Return a stable, type-namespaced selection id for selectable nodes, else None.

        Codes are unique per resource type within a dictionary; the ``class:``/``prop:``
        prefix keeps a class and a property that happen to share a code from colliding.
        """
        if node.bsdd_data is None:
            return None
        if node.node_type in (nc.CLASS_NODE_TYPE, nc.GOP_NODE_TYPE):
            return f"class:{node.bsdd_data.Code}"
        if node.node_type == nc.PROPERTY_NODE_TYPE:
            return f"prop:{node.bsdd_data.Code}"
        return None

    @classmethod
    def generate_node_info_data(cls, nodes: list[Node], bsdd_dictionary: BsddDictionary) -> str:
        """Build the JSON payload mapping each selectable node id to its display info.

        Each entry is ``{"name", "kind", "definition", "rows"}`` where ``rows`` is
        ``[[name, pset, datatype, desc], ...]`` (empty for properties). It is embedded
        verbatim into an inline script so the page needs no network access.
        """
        import json
        from bsdd_json.utils import property_utils as prop_utils

        data: dict[str, dict] = {}
        for node in nodes:
            select_id = cls._node_select_id(node)
            if select_id is None or select_id in data:
                continue
            bsdd_data = node.bsdd_data
            definition = bsdd_data.Definition or bsdd_data.Description or ""

            rows: list[list[str]] = []
            if node.node_type in (nc.CLASS_NODE_TYPE, nc.GOP_NODE_TYPE):
                kind = "Class"
                for cp in bsdd_data.ClassProperties:
                    prop = prop_utils.get_property_by_class_property(cp, bsdd_dictionary)
                    name = prop.Name if prop else (cp.PropertyCode or cp.PropertyUri or "")
                    pset = cp.PropertySet or ""
                    datatype = (prop.DataType if prop else None) or ""
                    description = cp.Description or (prop.Description if prop else None) or ""
                    rows.append([name, pset, datatype, description])
                rows.sort(key=lambda r: (r[1].lower(), r[0].lower()))
            else:
                kind = "Property"

            data[select_id] = {
                "name": bsdd_data.Name or bsdd_data.Code,
                "kind": kind,
                "definition": definition,
                "rows": rows,
            }

        # Escape "</" so the payload can never terminate the surrounding <script> element.
        return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    @classmethod
    def generate_node_legend(cls, nodes: list[Node]) -> str:
        # Legend — node types
        node_legend_html = ""
        seen_node_types = {n.node_type for n in nodes}
        for ntype in nc.ALLOWED_NODE_TYPES:
            if ntype not in seen_node_types:
                continue
            fill = cls._qcolor_to_css(nc.NODE_COLOR_MAP.get(ntype, nc.NODE_COLOR_DEFAULT))
            label_text = html.escape(nc.NODE_TYPE_LABEL_MAP.get(ntype, ntype))
            shape = nc.NODE_SHAPE_MAP.get(ntype, nc.SHAPE_STYLE_RECT)
            if shape == nc.SHAPE_STYPE_ELLIPSE:
                icon = (
                    f'<svg width="36" height="16" style="vertical-align:middle">'
                    f'<ellipse cx="18" cy="8" rx="17" ry="7" fill="{fill}" '
                    f'stroke="{constants.NODE_BORDER}" stroke-width="1"/></svg>'
                )
            elif shape == nc.SHAPE_STYLE_ROUNDED_RECT:
                icon = (
                    f'<svg width="36" height="16" style="vertical-align:middle">'
                    f'<rect x="1" y="1" width="34" height="14" rx="4" fill="{fill}" '
                    f'stroke="{constants.NODE_BORDER}" stroke-width="1"/></svg>'
                )
            else:
                icon = (
                    f'<svg width="36" height="16" style="vertical-align:middle">'
                    f'<rect x="1" y="1" width="34" height="14" fill="{fill}" '
                    f'stroke="{constants.NODE_BORDER}" stroke-width="1"/></svg>'
                )
            node_legend_html += f'<div class="legend-row">{icon}<span>{label_text}</span></div>'
        return node_legend_html

    @classmethod
    def generate_edge_legend(cls, edges: list[Edge]) -> str:
        # Legend — edge types
        edge_legend_html = ""
        seen_edge_types = {e.edge_type for e in edges}
        for etype in ec.ALLOWED_EDGE_TYPES:
            if etype not in seen_edge_types:
                continue
            style = ec.EDGE_STYLE_MAP.get(etype, ec.EDGE_STYLE_DEFAULT)
            color = cls._qcolor_to_css(style["color"])
            dash = cls._dash_array(style.get("style"))
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            label_text = html.escape(ec.EDGE_TYPE_LABEL_MAP.get(etype, etype))
            icon = (
                f'<svg width="36" height="16" style="vertical-align:middle">'
                f'<line x1="2" y1="8" x2="34" y2="8" stroke="{color}" '
                f'stroke-width="2"{dash_attr}/></svg>'
            )
            edge_legend_html += f'<div class="legend-row">{icon}<span>{label_text}</span></div>'
        return edge_legend_html

    @classmethod
    def generate_title(cls, bsdd_dictionary: BsddDictionary) -> tuple[str, str]:
        dict_title = ""
        if bsdd_dictionary:
            dict_title = html.escape(
                f"{bsdd_dictionary.OrganizationCode}/{bsdd_dictionary.DictionaryCode}"
                f" v{bsdd_dictionary.DictionaryVersion}"
            )
        page_title = f"bSDD Graph – {dict_title}" if dict_title else "bSDD Graph"
        heading_suffix = f" – {dict_title}" if dict_title else ""
        return page_title, heading_suffix

    # ---------------------------------------------------------------------------
    # Main entry point
    # ---------------------------------------------------------------------------
    @classmethod
    def generate_html(
        cls,
        page_title: str,
        heading_suffix: str,
        svg_w: float,
        svg_h: float,
        defs_parts: str,
        edge_parts: str,
        node_parts: str,
        node_legend_html: str,
        edge_legend_html: str,
        node_info_json: str = "{}",
    ) -> str:

        defs_block = f"<defs>{''.join(defs_parts)}</defs>" if defs_parts else ""
        bg_rect = f'<rect width="{svg_w:.0f}" height="{svg_h:.0f}" fill="{constants.SCENE_BG}"/>'
        svg_inner = "\n      ".join([defs_block, bg_rect] + edge_parts + node_parts)

        return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{page_title}</title>
    <style>
        body {{
        background: #0f1018;
        color: #e0e0e0;
        font-family: sans-serif;
        margin: 0;
        padding: 16px;
        box-sizing: border-box;
        }}
        h2 {{ margin: 0 0 12px; font-size: 1.1rem; color: #c0c8e0; }}
        .graph-wrap {{
        overflow: auto;
        border: 1px solid #2a3050;
        border-radius: 6px;
        max-height: 80vh;
        }}
        svg {{ display: block; }}
        a:hover .node-shape {{ filter: brightness(1.35); }}
        .selectable {{ cursor: pointer; }}
        .selectable:hover .node-shape {{ filter: brightness(1.35); }}
        .selectable.selected .node-shape {{ stroke: #ffffff; stroke-width: 2.5; }}
        .def-panel {{
        margin-top: 16px;
        background: #1a1d2e;
        border: 1px solid #2a3050;
        border-radius: 6px;
        padding: 12px;
        }}
        .def-panel h3 {{ margin: 0 0 8px; font-size: 1rem; color: #c0c8e0; }}
        .def-kind {{
        display: inline-block;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #0f1018;
        background: #7080a0;
        border-radius: 3px;
        padding: 1px 6px;
        margin-left: 8px;
        vertical-align: middle;
        }}
        #def-text {{ margin: 0; font-size: 13px; line-height: 1.5; color: #c8d0e0; white-space: pre-wrap; }}
        #def-text.def-empty {{ color: #7080a0; font-style: italic; }}
        .prop-panel {{
        margin-top: 16px;
        background: #1a1d2e;
        border: 1px solid #2a3050;
        border-radius: 6px;
        padding: 12px;
        }}
        .prop-panel h3 {{ margin: 0 0 10px; font-size: 1rem; color: #c0c8e0; }}
        .prop-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
        .prop-table th, .prop-table td {{
        text-align: left;
        padding: 6px 8px;
        border-bottom: 1px solid #2a3050;
        vertical-align: top;
        }}
        .prop-table th {{
        color: #7080a0;
        text-transform: uppercase;
        font-size: 10px;
        letter-spacing: 0.06em;
        }}
        .prop-table td {{ color: #c8d0e0; }}
        .prop-table tr:hover td {{ background: #20243a; }}
        .prop-empty {{ color: #7080a0; font-style: italic; }}
        .legend {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
        }}
        .legend-section {{
        background: #1a1d2e;
        border: 1px solid #2a3050;
        border-radius: 6px;
        padding: 8px 4px 4px;
        min-width: 180px;
        }}
        .legend-title {{
        font-size: 10px;
        color: #7080a0;
        margin: 0 8px 6px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        }}
        .legend-row {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 3px 8px;
        font-size: 12px;
        color: #c8d0e0;
        }}
    </style>
    </head>
    <body>
    <h2>bSDD Graph View{heading_suffix}</h2>
    <div class="graph-wrap">
        <svg xmlns="http://www.w3.org/2000/svg"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            width="{svg_w:.0f}" height="{svg_h:.0f}"
            viewBox="0 0 {svg_w:.0f} {svg_h:.0f}">
        {svg_inner}
        </svg>
    </div>
    <div class="legend">
        <div class="legend-section">
        <div class="legend-title">Node Types</div>
        {node_legend_html}
        </div>
        <div class="legend-section">
        <div class="legend-title">Relationship Types</div>
        {edge_legend_html}
        </div>
    </div>
    <div class="def-panel">
        <h3><span id="def-name">Definition</span><span id="def-kind" class="def-kind" hidden></span></h3>
        <p id="def-text" class="def-empty">Select a class or property node to view its definition.</p>
    </div>
    <div class="prop-panel">
        <h3 id="prop-title">Class Properties</h3>
        <table class="prop-table">
        <thead>
            <tr>
            <th>Property Name</th>
            <th>Property Set</th>
            <th>Data Type</th>
            <th>Description</th>
            </tr>
        </thead>
        <tbody id="prop-tbody">
            <tr><td class="prop-empty" colspan="4">Select a class node to view its properties.</td></tr>
        </tbody>
        </table>
    </div>
    <script>
    const NODE_INFO = {node_info_json};
    (function () {{
        const tbody = document.getElementById('prop-tbody');
        const title = document.getElementById('prop-title');
        const defName = document.getElementById('def-name');
        const defKind = document.getElementById('def-kind');
        const defText = document.getElementById('def-text');
        let selectedEl = null;

        function setEmpty(message) {{
        tbody.innerHTML = '';
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.className = 'prop-empty';
        td.colSpan = 4;
        td.textContent = message;
        tr.appendChild(td);
        tbody.appendChild(tr);
        }}

        function renderDefinition(data) {{
        defName.textContent = data.name;
        defKind.textContent = data.kind;
        defKind.hidden = false;
        if (data.definition) {{
            defText.textContent = data.definition;
            defText.classList.remove('def-empty');
        }} else {{
            defText.textContent = 'No definition available.';
            defText.classList.add('def-empty');
        }}
        }}

        function render(id) {{
        const data = NODE_INFO[id];
        if (!data) return;
        renderDefinition(data);
        if (data.kind !== 'Class') {{
            title.textContent = 'Class Properties';
            setEmpty('Select a class node to view its properties.');
            return;
        }}
        title.textContent = 'Class Properties \\u2013 ' + data.name;
        if (!data.rows.length) {{ setEmpty('This class has no properties.'); return; }}
        tbody.innerHTML = '';
        for (const row of data.rows) {{
            const tr = document.createElement('tr');
            for (const cell of row) {{
            const td = document.createElement('td');
            td.textContent = cell == null ? '' : cell;
            tr.appendChild(td);
            }}
            tbody.appendChild(tr);
        }}
        }}

        document.querySelectorAll('[data-node-id]').forEach(function (el) {{
        el.addEventListener('click', function (e) {{
            e.preventDefault();
            if (selectedEl) selectedEl.classList.remove('selected');
            el.classList.add('selected');
            selectedEl = el;
            render(el.getAttribute('data-node-id'));
        }});
        el.addEventListener('dblclick', function (e) {{
            e.preventDefault();
            const href = el.getAttribute('data-href');
            if (href) window.open(href, '_blank');
        }});
        }});
    }})();
    </script>
    </body>
    </html>"""

    @classmethod
    def write_html(cls, html_content: str, path: str, window: WindowTool):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html_content)
                text = QCoreApplication.translate("GraphViewer", "HTML exported: ") + str(path)
                window.set_status(text)

        except Exception as e:
            logging.exception("Failed to export HTML: %s", e)

    @classmethod
    def generate_empty_html(cls):
        return """<!DOCTYPE html><html><body>
            <p style='color:#ccc;background:#141520;padding:16px'>
            No visible nodes to export.</p></body></html>"""
