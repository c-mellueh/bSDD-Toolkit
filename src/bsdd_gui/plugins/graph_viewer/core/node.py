from __future__ import annotations
from typing import TYPE_CHECKING, Type
import webbrowser
from bsdd_json.utils import property_utils as prop_utils


from bsdd_gui.plugins.graph_viewer.module.node import constants
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import Qt, QRectF

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.node import ui
    from bsdd_json import BsddClass, BsddProperty
    from bsdd_gui.module.property_table_widget.ui import PropertyWidget

from bsdd_json import BsddClass,  BsddClassProperty


def connect_signals(
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
    scene_view: Type[gv_tool.SceneView],
    settings: Type[gv_tool.Settings],
    project: Type[tool.Project],
    window: Type[gv_tool.Window],
):
    node.signals.remove_edge_requested.connect(
        lambda e, s, ov, ap: edge.remove_edge(e, s, project.get(), ov, ap)
    )
    node.signals.node_created.connect(lambda n: node.get_properties().nodes.append(n))
    node.signals.node_created.connect(scene_view.add_item)
    settings.signals.widget_created.connect(lambda sw: add_settings(node, settings))
    node.signals.filter_changed.connect(
        lambda k, v: scene_view.apply_filters(edge.get_filters(), node.get_filters())
    )
    node.connect_internal_signals()

    def update_paths(change: QGraphicsItem.GraphicsItemChange, n: ui.Node):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for e in scene_view.get_scene().items():
                if isinstance(e, edge.get_edge_class()) and (e.start_node is n or e.end_node is n):
                    edge.requeste_path_update(e)

    node.signals.node_changed.connect(update_paths)

    scene_view.signals.clear_scene_requested.connect(lambda: clear_all_nodes(node, scene_view))
    window.signals.widget_closed.connect(node.clear)


def connect_to_project_signals(node: Type[gv_tool.Node], project: Type[tool.Project]):
    def handle_remove(bsdd_data):
        if isinstance(bsdd_data, BsddClassProperty):
            bsdd_data = prop_utils.get_internal_property(bsdd_data)
        if not bsdd_data:
            return
        active_node = node.get_node_from_bsdd_data(bsdd_data)
        if not active_node:
            return
        node.remove_node(active_node, project.get())

    node.connect_external_signal(project.signals.class_removed, handle_remove)
    node.connect_external_signal(project.signals.property_removed, handle_remove)
    node.connect_external_signal(project.signals.class_property_removed, handle_remove)


def disconnect_signals(node: Type[gv_tool.Node]):
    node.disconnect_external_signals()
    node.disconnect_internal_signals()


def clear_all_nodes(node: Type[gv_tool.Node], scene_view: Type[gv_tool.SceneView]):
    scene = scene_view.get_scene()
    for n in node.get_nodes():
        scene.removeItem(n)
    node.clear()


def add_settings(node: Type[gv_tool.Node], settings: Type[gv_tool.Settings]):
    widget = node.create_settings_widget()
    for row in node.create_node_toggles():
        widget.layout().addLayout(row)
    settings.add_content_widget(widget)


def node_double_clicked(
    node: ui.Node,
    property_table: Type[tool.PropertyTableWidget],
    class_tree: Type[tool.ClassTreeView],
    main_window: Type[tool.MainWindowWidget],
):
    if node.node_type == constants.CLASS_NODE_TYPE:
        bsdd_class: BsddClass = node.bsdd_data
        class_tree.select_and_expand(bsdd_class, main_window.get_class_view())
        main_window.get().raise_()
        main_window.get().activateWindow()

    elif node.node_type == constants.PROPERTY_NODE_TYPE:
        bsdd_property: BsddProperty = node.bsdd_data
        property_table.request_widget()
        widget: PropertyWidget = property_table.get_widgets()[-1]
        property_table.select_property(bsdd_property, widget.tv_properties)

    elif node.node_type in [
        constants.EXTERNAL_CLASS_NODE_TYPE,
        constants.EXTERNAL_PROPERTY_NODE_TYPE,
        constants.IFC_NODE_TYPE,
    ]:
        bsdd_class: BsddClass = node.bsdd_data
        uri = bsdd_class.OwnedUri
        if uri.startswith("http://") or uri.startswith("https://"):
            webbrowser.open(uri)


def paint_node_legend(node_legend: ui._NodeLegendIcon, node: Type[gv_tool.Node]):
    p = QPainter(node_legend)
    p.setRenderHint(QPainter.Antialiasing, True)
    rect = node_legend.rect().adjusted(2, 2, -2, -2)
    color = node.get_color(node_legend._node_type)
    shape = node.get_shape(node_legend._node_type)
    pen = QPen(color)
    pen.setCosmetic(True)
    p.setPen(pen)
    brush = QBrush(Qt.BrushStyle.SolidPattern)
    brush.setColor(color)
    p.setBrush(brush)
    if shape == constants.SHAPE_STYPE_ELLIPSE:
        p.drawEllipse(rect)
    elif shape == constants.SHAPE_STYLE_ROUNDED_RECT:
        p.drawRoundedRect(rect, 4, 4)
    else:
        p.drawRect(rect)


def paint_node(focus_node: ui.Node, painter: QPainter, node: Type[gv_tool.Node]):
    painter.setRenderHint(QPainter.Antialiasing)
    # Ensure our rectangle matches current text size and font
    node._update_size_for_text(focus_node, painter)
    painter.setPen(focus_node.border)
    painter.setBrush(
        focus_node.brush if not focus_node.isSelected() else QBrush(QColor(255, 180, 90))
    )
    rect = QRectF(-focus_node._w / 2, -focus_node._h / 2, focus_node._w, focus_node._h)
    if focus_node.node_shape == "ellipse":
        painter.drawEllipse(rect)
    elif focus_node.node_shape == "roundrect":
        painter.drawRoundedRect(rect, 6, 6)
    else:
        painter.drawRect(rect)
    painter.setPen(QPen(QColor(20, 20, 30)))
    painter.drawText(rect, Qt.AlignCenter, focus_node.label)
