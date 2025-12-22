from __future__ import annotations
from typing import TYPE_CHECKING
import logging

from bsdd_gui.presets.tool_presets import BaseTool
import bsdd_gui
from bsdd_gui.plugins.graph_viewer.module.buchheim import ui, trigger, constants
from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QCoreApplication, QPointF, Signal,QObject

if TYPE_CHECKING:
    from bsdd_gui.plugins.graph_viewer.module.buchheim.prop import GraphViewerBuchheimProperties
    from bsdd_gui.plugins.graph_viewer.module.edge.ui import Edge
    from bsdd_gui.plugins.graph_viewer.module.node.ui import Node


class Signals(QObject):
    buchheim_requested = Signal()


class Buchheim(BaseTool):
    signals = Signals()

    @classmethod
    def get_properties(cls) -> GraphViewerBuchheimProperties:
        return bsdd_gui.GraphViewerBuchheimProperties

    @classmethod
    def _get_trigger(cls):
        return trigger

    @classmethod
    def request_tree_creation(cls):
        cls.signals.buchheim_requested.emit()

    @classmethod
    def connect_internal_signals(cls):
        cls.signals.buchheim_requested.connect(trigger.create_tree)
        return super().connect_internal_signals()

    @classmethod
    def reset_children_dict(cls, nodes: list[Node], edges: list[Edge], active_edge_type: str):
        if not active_edge_type:
            return False
        children_dict = dict()  # list all children
        parent_dict = {node: None for node in nodes}

        for edge in edges:
            if edge.edge_type != active_edge_type:
                continue
            start_node = edge.start_node
            end_node = edge.end_node
            parent_dict[start_node] = end_node
            if end_node not in children_dict:
                children_dict[end_node] = list()
            children_dict[end_node].append(start_node)
        cls.get_properties().children_dict = children_dict
        cls.get_properties().parent_dict = parent_dict
        return True

    @classmethod
    def find_roots(cls, nodes: list[Node]) -> list[Node]:
        roots = list()
        for node in nodes:
            if cls.parent(node) is None:
                roots.append(node)
        return roots

    @classmethod
    def create_information(cls, parent_widget: QWidget):
        # Inform the user that an edge type must be selected
        try:
            title = QCoreApplication.translate("GraphView", "Create Tree")
            msg = QCoreApplication.translate(
                "GraphView",
                "Select an edge type in the sidebar (Edge Types) by double-clicking the legend to activate it, then run Create Tree.",
            )
            QMessageBox.information(parent_widget, title, msg)
        except Exception:
            pass

    @classmethod
    def intialize(cls, v: Node, depth=0, number: int = 1):
        v.thread = None
        v._lmost_sibling = None
        v.mod = 0
        v.change = 0
        v.shift = 0
        v.ancestor = v
        v.number = None
        cls.get_properties().position_dict[v] = [-1.0, depth]
        v.number = number
        for index, w in enumerate(cls.children(v)):
            cls.intialize(w, depth + 1, index + 1)

    @classmethod
    def buchheim(cls, v: Node):
        tree = cls.firstwalk(v, 0)
        cls.second_walk(tree)
        return tree

    @classmethod
    def firstwalk(cls, v: Node, depth):
        while depth >= len(cls.get_properties().height_list):
            cls.get_properties().height_list.append(0.0)
        cls.get_properties().height_list[depth] = max(
            cls.get_properties().height_list[depth], cls.height(v)
        )

        if len(cls.children(v)) == 0:  # no children exist
            # If a left brother exists, place next to it; otherwise start at 0
            lbrother = cls.lbrother(v)
            if lbrother:
                sibling_sep = (cls.width(lbrother) + cls.width(v)) / 2.0 + constants.X_MARGIN
                cls.set_x(v, cls.x(lbrother) + sibling_sep)
            else:
                cls.set_x(v, 0.0)

        else:
            default_ancestor = cls.children(v)[0]  # elektrotechnik
            for w in cls.children(v):
                cls.firstwalk(w, depth + 1)
                default_ancestor = cls.apportion(w, default_ancestor)
            c1 = cls.x(cls.children(v)[0])
            c2 = cls.x(cls.children(v)[-1])
            midpoint = (c1 + c2) / 2

            w = cls.lbrother(v)
            if w:
                # Align current subtree next to its left brother with symmetric spacing
                sibling_sep = (cls.width(w) + cls.width(v)) / 2.0 + constants.X_MARGIN
                new_x = cls.x(w) + sibling_sep
                cls.set_x(v, new_x)
                v.mod = new_x - midpoint
            else:
                cls.set_x(v, midpoint)
        return v

    @classmethod
    def second_walk(cls, v: Node, m=0, depth=0):
        cls.set_x(v, cls.x(v) + m)
        height_list = cls.get_properties().height_list
        cls.set_y(v, sum(height_list[:depth]) + constants.Y_MARGIN * depth)
        for w in cls.children(v):
            cls.second_walk(w, m + v.mod, depth + 1)

    @classmethod
    def apportion(cls, v: Node, default_ancestor: Node):
        w = cls.lbrother(v)
        if w is None:
            return default_ancestor
        # in buchheim notation:
        # i == inner; o == outer; r == right; l == left; r = +; l = -
        vir = vor = v
        vil = w
        vol = cls.get_lmost_sibling(v)
        sir = sor = v.mod
        sil = vil.mod
        sol = vol.mod
        while cls.right(vil) and cls.left(vir):
            vil = cls.right(vil)
            vir = cls.left(vir)
            vol = cls.left(vol)
            vor = cls.right(vor)
            vor.ancestor = v
            # Use both nodes' half-widths to avoid overlap and enforce a symmetric margin
            sep = (cls.width(vil) + cls.width(vir)) / 2.0 + constants.X_MARGIN * 2
            shift = (cls.x(vil) + sil) - (cls.x(vir) + sir) + sep
            if shift > 0:
                cls.move_subtree(cls.ancestor(vil, v, default_ancestor), v, shift)
                sir = sir + shift
                sor = sor + shift
            sil += vil.mod
            sir += vir.mod
            sol += vol.mod
            sor += vor.mod
        if cls.right(vil) and not cls.right(vor):
            vor.thread = cls.right(vil)
            vor.mod += sil - sor
        if cls.left(vir) and not cls.left(vol):
            vol.thread = cls.left(vir)
            vol.mod += sir - sol
            default_ancestor = v
        return default_ancestor

    @classmethod
    def move_subtree(cls, wl: Node, wr: Node, shift: float):
        subtrees = (wr.number or 0) - (wl.number or 0)
        if subtrees <= 0:
            subtrees = 1
        wr.change -= shift / subtrees
        wr.shift += shift
        wl.change += shift / subtrees
        cls.set_x(wr, cls.x(wr) + shift)
        wr.mod += shift

    @classmethod
    def ancestor(
        cls,
        vil: Node,
        v: Node,
        default_ancestor: Node,
    ):
        pv = cls.parent(v)
        siblings = cls.children(pv) if pv else []
        if vil.ancestor in siblings:
            return vil.ancestor
        else:
            return default_ancestor

    @classmethod
    def rearrange(cls, root_node: Node, base_pos: QPointF):
        def ra(v: Node):
            x, y = cls.pos(v)
            x = base_pos.x() + x
            y = base_pos.y() + y
            v.setPos(QPointF(x, y))
            for child in cls.children(v):
                ra(child)

        ra(root_node)

    # NodeProxy getter functions

    @classmethod
    def children(cls, v: Node) -> list[Node]:
        # Preserve original insertion order from children_dict; sorting by x corrupts numbering
        return cls.get_properties().children_dict.get(v, [])

    @classmethod
    def parent(cls, v: Node) -> Node:
        return cls.get_properties().parent_dict.get(v)

    @classmethod
    def left(cls, v: Node):
        if v.thread:
            return v.thread
        ch = cls.children(v)
        return ch[0] if ch else None

    @classmethod
    def right(cls, v: Node):
        if v.thread:
            return v.thread
        ch = cls.children(v)
        return ch[-1] if ch else None

    @classmethod
    def lbrother(cls, v: Node):
        n = None
        parent = cls.parent(v)
        if parent:
            for node in cls.children(parent):
                if node == v:
                    return n
                else:
                    n = node
        return n

    @classmethod
    def get_lmost_sibling(cls, v: Node) -> Node:
        p = cls.parent(v)
        if not p:
            return v
        ch = cls.children(p)
        if not ch:
            return v
        first = ch[0]
        if v._lmost_sibling is None:
            v._lmost_sibling = first
        return v if v == first else v._lmost_sibling

    @classmethod
    def x(cls, v: Node):
        return cls.get_properties().position_dict[v][0]

    @classmethod
    def y(cls, v: Node):
        return cls.get_properties().position_dict[v][1]

    @classmethod
    def set_x(cls, v: Node, x: float):
        cls.get_properties().position_dict[v][0] = x

    @classmethod
    def set_y(cls, v: Node, y: float):
        cls.get_properties().position_dict[v][1] = y

    @classmethod
    def pos(cls, v: Node):
        return cls.get_properties().position_dict[v]

    @classmethod
    def width(cls, v: Node):
        return v._w or 24.0

    @classmethod
    def height(cls, v: Node):
        return v._h or 24.0
