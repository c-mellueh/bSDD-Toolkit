from __future__ import annotations
from typing import TYPE_CHECKING, Type
import webbrowser


from bsdd_gui.plugins.graph_viewer.module.node import constants

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.node import ui
    from bsdd_json import BsddClass, BsddProperty
    from bsdd_gui.module.property_table_widget.ui import PropertyWidget


def connect_signals(
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
):
    node.signals.remove_edge_requested.connect(
        lambda e, s, ov, ap: edge.remove_edge(
            e,
            s,
            project.get(),
            ov,
            ap,
        )
    )

    node.signals.node_created.connect(lambda n: node.get_properties().nodes.append(n))
    node.signals.node_created.connect(scene_view.add_item)


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
