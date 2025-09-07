from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import *
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from typing import TYPE_CHECKING
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsObject,
    QGraphicsPathItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QSlider,
    QToolBar,
    QToolButton,
    QFileDialog,
)

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge


class QuadTree:
    def __init__(self, x, y, w, h, capacity=1):
        self.boundary = (x, y, w, h)
        self.capacity = capacity
        self.points: List[Tuple[Node, float, float]] = []
        self.divided = False
        self.total_mass = 0.0
        self.com_x = 0.0
        self.com_y = 0.0

    def insert(self, node: Node):
        x, y, w, h = self.boundary
        px, py = node.pos().x(), node.pos().y()
        if not (x <= px < x + w and y <= py < y + h):
            return False
        if len(self.points) < self.capacity and not self.divided:
            self.points.append((node, px, py))
            return True
        if not self.divided:
            self.subdivide()
        return (
            self.nw.insert(node)
            or self.ne.insert(node)
            or self.sw.insert(node)
            or self.se.insert(node)
        )

    def subdivide(self):
        x, y, w, h = self.boundary
        hw, hh = w / 2, h / 2
        self.nw = QuadTree(x, y, hw, hh)
        self.ne = QuadTree(x + hw, y, hw, hh)
        self.sw = QuadTree(x, y + hh, hw, hh)
        self.se = QuadTree(x + hw, y + hh, hw, hh)
        self.divided = True

    def compute_mass_distribution(self):
        if not self.divided:
            if not self.points:
                self.total_mass = 0.0
                return
            self.total_mass = len(self.points)
            self.com_x = sum(px for _, px, _ in self.points) / len(self.points)
            self.com_y = sum(py for _, _, py in self.points) / len(self.points)
        else:
            self.nw.compute_mass_distribution()
            self.ne.compute_mass_distribution()
            self.sw.compute_mass_distribution()
            self.se.compute_mass_distribution()
            children = [self.nw, self.ne, self.sw, self.se]
            self.total_mass = sum(c.total_mass for c in children)
            if self.total_mass > 0:
                self.com_x = sum(c.com_x * c.total_mass for c in children) / self.total_mass
                self.com_y = sum(c.com_y * c.total_mass for c in children) / self.total_mass

    def apply_force(self, node: Node, theta: float, k_repulsion: float) -> QPointF:
        if self.total_mass == 0:
            return QPointF(0, 0)
        x, y, w, h = self.boundary
        px, py = node.pos().x(), node.pos().y()
        dx, dy = self.com_x - px, self.com_y - py
        dist2 = dx * dx + dy * dy + 1e-9
        d = math.sqrt(dist2)
        if (w / d) < theta or not self.divided:
            force_mag = k_repulsion * self.total_mass / dist2
            return QPointF(force_mag * dx / d, force_mag * dy / d)
        else:
            f = QPointF(0, 0)
            f += self.nw.apply_force(node, theta, k_repulsion)
            f += self.ne.apply_force(node, theta, k_repulsion)
            f += self.sw.apply_force(node, theta, k_repulsion)
            f += self.se.apply_force(node, theta, k_repulsion)
            return f


# ----------------------------
# Physics engine with Barnes–Hut
# ----------------------------
class Physics:
    class QuadNode:
        __slots__ = (
            "cx",
            "cy",
            "half",
            "mass",
            "com_x",
            "com_y",
            "body",
            "bodies",
            "nw",
            "ne",
            "sw",
            "se",
        )

        def __init__(self, cx: float, cy: float, half: float):
            self.cx = cx
            self.cy = cy
            self.half = half
            self.mass = 0.0
            self.com_x = 0.0
            self.com_y = 0.0
            self.body: Optional[Node] = None
            self.bodies: Optional[List[Node]] = None  # for degenerate leaves
            self.nw = self.ne = self.sw = self.se = None

        def is_leaf(self) -> bool:
            return self.nw is None and self.ne is None and self.sw is None and self.se is None

        def _child_for(self, x: float, y: float):
            east = x >= self.cx
            north = y < self.cy
            return ("ne" if east else "nw") if north else ("se" if east else "sw")

        def _ensure_child(self, quadrant: str):
            h2 = self.half * 0.5
            if quadrant == "nw" and self.nw is None:
                self.nw = Physics.QuadNode(self.cx - h2, self.cy - h2, h2)
            elif quadrant == "ne" and self.ne is None:
                self.ne = Physics.QuadNode(self.cx + h2, self.cy - h2, h2)
            elif quadrant == "sw" and self.sw is None:
                self.sw = Physics.QuadNode(self.cx - h2, self.cy + h2, h2)
            elif quadrant == "se" and self.se is None:
                self.se = Physics.QuadNode(self.cx + h2, self.cy + h2, h2)

        def _add_mass(self, x: float, y: float, m: float):
            total = self.mass + m
            if total == 0:
                return
            self.com_x = (self.com_x * self.mass + x * m) / total if self.mass > 0 else x
            self.com_y = (self.com_y * self.mass + y * m) / total if self.mass > 0 else y
            self.mass = total

        def insert(self, node: Node, x: float, y: float, m: float = 1.0):
            # Update center-of-mass for this region
            self._add_mass(x, y, m)

            if self.is_leaf():
                # If we already collapsed into a degenerate leaf, just add here
                if self.bodies is not None:
                    if node not in self.bodies:
                        self.bodies.append(node)
                    return
                if self.body is None:
                    # empty leaf: store body here
                    self.body = node
                    return
                if self.body is node:
                    # same body being re-inserted; nothing to do
                    return

                # Check for degeneracy: points too close or cell too small
                old = self.body
                oldx, oldy = old.pos().x(), old.pos().y()
                dx = abs(oldx - x)
                dy = abs(oldy - y)
                POS_EPS = 1e-9
                MIN_HALF = 1e-6
                too_close = (dx <= POS_EPS and dy <= POS_EPS) or (self.half <= MIN_HALF)
                if too_close:
                    # Collapse to a list of bodies within this leaf to avoid infinite subdivision
                    self.bodies = [old, node] if old is not node else [old]
                    self.body = None
                    return

                # Subdivide and reinsert the existing body
                self.body = None
                quadrant_old = self._child_for(oldx, oldy)
                self._ensure_child(quadrant_old)
                getattr(self, quadrant_old).insert(old, oldx, oldy, 1.0)

            # Insert new body into a child
            quadrant = self._child_for(x, y)
            self._ensure_child(quadrant)
            getattr(self, quadrant).insert(node, x, y, m)

        def compute_force(
            self,
            target: Node,
            tx: float,
            ty: float,
            theta: float,
            k_repulsion: float,
            eps: float = 0.01,
        ) -> Tuple[float, float]:
            if self.mass == 0.0:
                return 0.0, 0.0
            # If this region is just the target itself, ignore
            if self.is_leaf():
                if self.bodies is not None:
                    # Compute exact pairwise repulsion within a degenerate leaf
                    fx = fy = 0.0
                    for b in self.bodies:
                        if b is target:
                            continue
                        bx, by = b.pos().x(), b.pos().y()
                        dx = tx - bx
                        dy = ty - by
                        d2 = dx * dx + dy * dy + eps
                        d = math.sqrt(d2)
                        f_mag = k_repulsion / d2
                        fx += f_mag * (dx / d)
                        fy += f_mag * (dy / d)
                    return fx, fy
                if self.body is target:
                    return 0.0, 0.0

            dx = tx - self.com_x
            dy = ty - self.com_y
            d2 = dx * dx + dy * dy + eps
            d = math.sqrt(d2)
            size = self.half * 2.0

            # Accept this node as an aggregate mass
            if self.is_leaf() or (size / d) < theta:
                f_mag = k_repulsion * self.mass / d2
                return f_mag * (dx / d), f_mag * (dy / d)

            fx = fy = 0.0
            for child in (self.nw, self.ne, self.sw, self.se):
                if child is not None:
                    cfx, cfy = child.compute_force(target, tx, ty, theta, k_repulsion, eps)
                    fx += cfx
                    fy += cfy
            return fx, fy

    def __init__(self):
        # Tunables (good defaults)
        self.k_repulsion = 1600.0  # Coulomb-like constant
        self.k_spring = 0.01  # Hooke spring constant
        self.spring_length = 200.0  # ideal edge length (px)
        self.damping = 0.85  # velocity damping [0..1]
        self.max_step = 30.0  # clamp max displacement per tick
        self.gravity_center = QPointF(0.0, 0.0)
        self.gravity_strength = 0.0  # no pull to scene center (spread out)

        # Barnes–Hut parameters
        self.use_barnes_hut = True
        self.bh_theta = 0.7  # smaller = more accurate, slower
        self.bh_min_size = 12  # switch to BH when nodes >= this

    def _build_quadtree(self, nodes: List[Node]) -> Optional["Physics.QuadNode"]:
        if not nodes:
            return None
        xs = [n.pos().x() for n in nodes]
        ys = [n.pos().y() for n in nodes]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        cx = (minx + maxx) * 0.5
        cy = (miny + maxy) * 0.5
        size = max(maxx - minx, maxy - miny)
        half = max(1.0, size * 0.5 + 1.0)
        root = Physics.QuadNode(cx, cy, half)
        for n in nodes:
            p = n.pos()
            root.insert(n, p.x(), p.y(), 1.0)
        return root

    def step(self, nodes: List[Node], edges: List[Edge], dt: float = 1.0):
        # Accumulate forces per node
        forces: Dict[Node, QPointF] = {n: QPointF(0.0, 0.0) for n in nodes}

        # Repulsion: Barnes–Hut or pairwise
        if self.use_barnes_hut and len(nodes) >= self.bh_min_size:
            root = self._build_quadtree(nodes)
            if root is not None:
                for n in nodes:
                    p = n.pos()
                    fx, fy = root.compute_force(
                        n, p.x(), p.y(), self.bh_theta, self.k_repulsion, eps=0.01
                    )
                    forces[n] += QPointF(fx, fy)
        else:
            # Pairwise O(N^2)
            for i in range(len(nodes)):
                ni = nodes[i]
                pi = ni.pos()
                for j in range(i + 1, len(nodes)):
                    nj = nodes[j]
                    pj = nj.pos()
                    delta = pi - pj
                    dist2 = max(0.01, delta.x() * delta.x() + delta.y() * delta.y())
                    force_mag = self.k_repulsion / dist2
                    d = math.sqrt(dist2)
                    fx = force_mag * (delta.x() / d)
                    fy = force_mag * (delta.y() / d)
                    forces[ni] += QPointF(fx, fy)
                    forces[nj] -= QPointF(fx, fy)

        # Edge springs
        for e in edges:
            a, b = e.start_node, e.end_node
            delta = b.pos() - a.pos()
            d = math.hypot(delta.x(), delta.y()) or 0.0001
            force_mag = self.k_spring * (d - self.spring_length) * e.weight
            fx = force_mag * (delta.x() / d)
            fy = force_mag * (delta.y() / d)
            forces[a] += QPointF(fx, fy)
            forces[b] -= QPointF(fx, fy)

        # Optional gravity towards center (disabled by default)
        if self.gravity_strength != 0.0:
            for n in nodes:
                delta = self.gravity_center - n.pos()
                forces[n] += QPointF(
                    delta.x() * self.gravity_strength, delta.y() * self.gravity_strength
                )

        # Integrate velocities and positions
        for n in nodes:
            if n.fixed or n.isUnderMouse():
                n.velocity *= 0
                continue
            v = n.velocity + forces[n] * dt
            v *= self.damping
            step_len = math.hypot(v.x(), v.y())
            if step_len > self.max_step:
                v *= self.max_step / step_len
            n.velocity = v
            old_pos = n.pos()
            n.setPos(old_pos + v)
            np = n.pos()
