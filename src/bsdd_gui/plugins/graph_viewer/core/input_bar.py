from __future__ import annotations

from typing import TYPE_CHECKING, Type
from PySide6.QtCore import QPointF
from random import random
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json.utils import class_utils
from bsdd_json.utils import property_utils as prop_utils

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.input_bar import ui


def connect_signals(input_bar: Type[gv_tool.InputBar], window: Type[gv_tool.Window]):
    # window.signals.widget_created.connect(lambda *_: input_bar.request_widget)
    input_bar.connect_internal_signals()


def create_widget(input_bar: Type[gv_tool.InputBar]):
    input_bar.create_widget()


def register_widget(
    widget: ui.InputBar, input_bar: Type[gv_tool.InputBar], window: Type[gv_tool.Window]
):
    input_bar.register_widget(widget)
    # window.get_widget().layout().insertWidget(0,widget)


def connect_widget(widget: ui.InputBar, input_bar: Type[gv_tool.InputBar]):
    input_bar.connect_widget_signals(widget)


def add_node_by_lineinput(
    input_bar: Type[gv_tool.InputBar],
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    project: Type[tool.Project],
):
    text = input_bar.get_text()
    view = scene_view.get_view()
    bsdd_class, bsdd_property = None, None
    scene_pos = view.mapToScene(view.viewport().rect().center())
    offset = QPointF(random() * 100, random() * 100)
    scene_pos += offset  # slight random offset to avoid exact overlap
    if not text:
        return

    uri_dict = node.get_uri_dict(project.get())

    if dict_utils.is_uri(text):
        if text in uri_dict:
            return
        is_external = dict_utils.is_external_ref(text, project.get())
        resource_type = dict_utils.parse_bsdd_url(text).get("resource_type")

        if resource_type == "class":
            bsdd_class = class_utils.get_class_by_uri(project.get(), text)
            if is_external:
                node.add_node(bsdd_class, pos=scene_pos, is_external=True)
            else:
                scene_view.request_classes_insert([bsdd_class], scene_pos)

        elif resource_type == "prop":
            bsdd_property = prop_utils.get_property_by_uri(text, project.get())
            if is_external:
                node.add_node(bsdd_property, pos=scene_pos, is_external=is_external)
            else:
                scene_view.request_properties_insert([bsdd_property], scene_pos)
        else:
            return
    else:
        bsdd_class = class_utils.get_class_by_code(project.get(), text)
        bsdd_property = prop_utils.get_property_by_code(text, project.get())

        if bsdd_class:
            if class_utils.build_bsdd_uri(bsdd_class, project.get()) in uri_dict:
                return
            scene_view.request_classes_insert([bsdd_class], scene_pos)

        elif bsdd_property:
            if prop_utils.build_bsdd_uri(bsdd_property, project.get()) in uri_dict:
                return
            scene_view.request_properties_insert([bsdd_property], scene_pos)
        else:
            return
    scene_view.request_recalculate_edges()
    input_bar.clear()
