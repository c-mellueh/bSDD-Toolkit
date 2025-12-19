from __future__ import annotations
from typing import TYPE_CHECKING
import logging
from bsdd_json import BsddDictionary
import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.edge import ui, trigger, constants

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.scene_view.ui import GraphScene
    from bsdd_gui.plugins.graph_viewer.module.edge.prop import GraphViewerEdgeProperties


class Signals:
    pass


class Edge:
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerEdgeProperties:
        return bsdd_gui.GraphViewerEdgeProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def remove_edge(
        cls,
        edge: ui.Edge,
        scene: GraphScene,
        bsdd_dictionary: BsddDictionary,
        only_visual=False,
        allow_parent_deletion=False,
    ):
        pass

    # TODO
    # if edge is None:
    #     return

    # start_node, end_node = edge.start_node, edge.end_node
    # relation_type = edge.edge_type
    # if relation_type == constants.GENERIC_REL:
    #     return

    # if relation_type == constants.PARENT_CLASS and not allow_parent_deletion:
    #     return

    # if not scene:
    #     return
    # try:
    #     scene.removeItem(edge)
    # except Exception:
    #     pass
    # try:
    #     if edge in scene.edges:
    #         scene.edges.remove(edge)
    # except ValueError:
    #     pass
    # if only_visual:
    #     return
    # start_data, end_data = start_node.bsdd_data, end_node.bsdd_data

    # if isinstance(start_data, BsddClass):
    #     if isinstance(end_data, BsddClass):
    #         if relation_type == constants.IFC_REFERENCE_REL:
    #             start_data.RelatedIfcEntityNamesList.remove(end_data.Code)
    #             cls.signals.ifc_reference_removed.emit(start_data, end_data.Code)
    #         else:
    #             class_relation = cl_utils.get_class_relation(
    #                 start_data, end_data, relation_type
    #             )
    #             if not class_relation:
    #                 return
    #             start_data.ClassRelations.remove(class_relation)
    #             cls.signals.edge_removed.emit(edge)
    #             cls.signals.class_relation_removed.emit(class_relation)
    #     elif isinstance(end_data, BsddProperty):
    #         if end_node.is_external:
    #             class_property = {
    #                 cp.PropertyUri: cp for cp in start_data.ClassProperties if cp.PropertyUri
    #             }.get(end_data.OwnedUri)
    #         else:
    #             class_property = {cp.PropertyCode: cp for cp in start_data.ClassProperties}.get(
    #                 end_data.Code
    #             )
    #         if class_property is None:
    #             return
    #         start_data.ClassProperties.remove(class_property)
    #         cls.signals.class_property_removed.emit(class_property, start_data)

    # elif isinstance(start_data, BsddProperty):
    #     if isinstance(end_data, BsddProperty):
    #         if end_node.is_external:
    #             end_uri = end_data.OwnedUri
    #         else:
    #             end_uri = prop_utils.build_bsdd_uri(end_data, bsdd_dictionary)
    #         property_relation = prop_utils.get_property_relation(
    #             start_data, end_uri, relation_type
    #         )
    #         if not property_relation:
    #             return
    #         start_data.PropertyRelations.remove(property_relation)
    #         cls.signals.property_relation_removed.emit(property_relation)

    #         cls.signals.edge_removed.emit(edge)
    #     elif isinstance(end_data, BsddClass):
    #         class_property = {cp.PropertyCode: cp for cp in end_data.ClassProperties}.get(
    #             start_data.Code
    #         )
    #         if class_property is None:
    #             return
    #         end_data.ClassProperties.remove(class_property)
    #         cls.signals.class_property_removed.emit(class_property, end_data)
