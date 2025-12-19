from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from bsdd_gui import tool
    from bsdd_gui.plugins.graph_viewer import tool as gv_tool
    from bsdd_gui.plugins.graph_viewer.module.scene_view import ui
    from bsdd_gui.plugins.graph_viewer.module.window import ui as ui_window


def connect_signals(window: Type[gv_tool.Window], scene_view: Type[gv_tool.SceneView]):
    window.signals.widget_created.connect(lambda w: handle_widget_creation(w, scene_view))
    window.signals.toggle_running_requested.connect(scene_view.toggle_running)
    window.signals.delete_selection_requested.connect(scene_view.request_delete_selection)


def handle_widget_creation(widget: ui_window.GraphWidget, scene_view: Type[gv_tool.SceneView]):
    scene_view.set_view(widget.view)
    widget.view.setScene(scene_view.create_scene())
    scene_view.create_help_overlay()
    scene_view.connect_view()


def delete_selection(
    scene_view: Type[gv_tool.SceneView],
    project: Type[tool.Project],
    edge: Type[gv_tool.Edge],
    node: Type[gv_tool.Node],
):
    scene = scene_view.get_scene()
    bsdd_dictionary = project.get()
    selected_nodes, selected_edges = scene_view.get_selected_items()
    edges_to_remove = list(set(selected_edges))
    for e in edges_to_remove:
        edge.remove_edge(edge, scene, bsdd_dictionary)

    for n in selected_nodes:
        node.remove_node(n, scene, ignored_edges=edges_to_remove)


def resize_event(event, scene_view: Type[gv_tool.SceneView]):
    scene_view.reposition_help_overlay()


def mouse_press_event(
    event: QMouseEvent,
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    try:
        pos_view = scene_view._event_qpoint(event)
        pos_scene = view.mapToScene(pos_view)
    except Exception:
        pass

    middle_pressed = event.button() == Qt.MouseButton.MiddleButton
    left_clicked = event.button() == Qt.MouseButton.LeftButton
    shift_pressed = event.modifiers() & Qt.KeyboardModifier.ShiftModifier

    if middle_pressed:
        # Start manual panning with middle mouse
        scene_view.set_panning_mmb(True)
        scene_view.set_pan_last_pos(scene_view._event_qpoint(event))
        try:
            view.setCursor(Qt.CursorShape.ClosedHandCursor)
        except Exception:
            pass
        event.accept()
        return

    elif left_clicked and shift_pressed:
        # Begin edge drawing if pressed on a Node
        pos_view = scene_view._event_qpoint(event)
        item = scene_view._item_at_pos(pos_view)
        n = node._node_from_item(item)
        if n is None:
            return
        scene_pos = view.mapToScene(pos_view)
        edge._start_edge_drag(n, scene_pos)
        event.accept()


def mouse_release_event(
    event: QMouseEvent,
    scene_view: Type[gv_tool.SceneView],
    node: Type[gv_tool.Node],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    if scene_view.get_panning_mmb() and event.button() == Qt.MiddleButton:
        scene_view.set_panning_mmb(False)
        scene_view.set_pan_last_pos(None)
        try:
            view.setCursor(Qt.ArrowCursor)
        except Exception:
            pass
        event.accept()
        return
    elif edge.is_edge_drag_active() and event.button() == Qt.LeftButton:
        pos_view = scene_view._event_qpoint(event)
        item = scene_view._item_at_pos(pos_view)
        n = node._node_from_item(item)
        edge._finish_edge_drag(n)
        event.accept()
        return


def mouse_move_event(
    event: QMouseEvent,
    scene_view: Type[gv_tool.SceneView],
    edge: Type[gv_tool.Edge],
):
    view = scene_view.get_view()
    if scene_view.get_panning_mmb():
        # Drag the view by adjusting scrollbars
        cur = scene_view._event_qpoint(event)
        if scene_view.get_pan_last_pos() is not None and cur is not None:
            delta = cur - scene_view.get_pan_last_pos()
            try:
                view.horizontalScrollBar().setValue(
                    view.horizontalScrollBar().value() - int(delta.x())
                )
                view.verticalScrollBar().setValue(view.verticalScrollBar().value() - int(delta.y()))
            except Exception:
                pass
        scene_view.set_pan_last_pos(cur)
        event.accept()
        return
    if edge.is_edge_drag_active():
        pos_view = scene_view._event_qpoint(event)
        scene_pos = view.mapToScene(pos_view)
        edge._update_edge_drag(scene_pos)
        event.accept()
        return
