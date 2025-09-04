from __future__ import annotations
from bsdd_json.utils import class_utils as cl_utils
from bsdd_json.utils import property_utils as prop_utils
from bsdd_json.utils import dictionary_utils as dict_utils
from bsdd_json import *
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

from PySide6.QtCore import (
    QPointF,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,

)
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
    QFileDialog
)


# ----------------------------
# Data structures
# ----------------------------
@dataclass
class EdgeData:
    a: "Node"
    b: "Node"
    weight: float = 1.0


class Edge(QGraphicsPathItem):

    def __init__(
        self, a: "Node", b: "Node", weight: float = 1.0, edge_type: str = "generic"
    ):
        super().__init__()
        self.a = a
        self.b = b
        self.weight = weight
        self.edge_type = edge_type
        self.setZValue(-1)
        pen = QPen(QColor(130, 130, 150), 1.5)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.update_path()

    def update_path(self):
        path = QPainterPath()
        path.moveTo(self.a.pos())
        path.lineTo(self.b.pos())
        self.setPath(path)


class Node(QGraphicsObject):

    def __init__(
        self,
        label: str,
        radius: float = 12.0,
        color: QColor | None = None,
        node_type: str = "generic",
    ):
        super().__init__()
        self.label = label
        # radius retained for backward-compat, not used for drawing
        self.radius = radius
        self.color = color or QColor(80, 140, 255)
        self.brush = QBrush(self.color)
        self.border = QPen(QColor(40, 60, 90), 1.2)
        self.border.setCosmetic(True)
        self.node_type = node_type

        self.velocity = QPointF(0.0, 0.0)
        self.fixed = False

        # Padding around text inside the rectangle
        self.pad_x = 10.0
        self.pad_y = 6.0
        # Initial size; refined on first paint using actual font metrics
        try:
            fm = QFontMetrics(QApplication.font())
            tr = fm.boundingRect(self.label)
            self._w = max(2 * self.radius, tr.width() + 2 * self.pad_x)
            self._h = max(2 * self.radius, tr.height() + 2 * self.pad_y)
        except Exception:
            # Fallback if no application font is available yet
            self._w = self._h = 2 * self.radius

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
            | QGraphicsItem.ItemIsSelectable
        )
        self.setAcceptHoverEvents(True)

    def boundingRect(self) -> QRectF:
        # Include a small margin for the border
        margin = 2.0
        return QRectF(-self._w / 2 - margin, -self._h / 2 - margin, self._w + 2 * margin, self._h + 2 * margin)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(QRectF(-self._w / 2, -self._h / 2, self._w, self._h))
        return path

    def _update_size_for_text(self, painter: Optional[QPainter] = None):
        # Compute size from current font metrics so the rectangle fits the text
        try:
            fm = painter.fontMetrics() if painter is not None else QFontMetrics(QApplication.font())
        except Exception:
            return  # can't compute metrics safely right now
        tr = fm.boundingRect(self.label)
        new_w = tr.width() + 2 * self.pad_x
        new_h = tr.height() + 2 * self.pad_y
        # Avoid excessive geometry changes for tiny fluctuations
        if abs(new_w - self._w) > 0.5 or abs(new_h - self._h) > 0.5:
            self.prepareGeometryChange()
            self._w = new_w
            self._h = new_h

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        # Ensure our rectangle matches current text size and font
        self._update_size_for_text(painter)
        painter.setPen(self.border)
        painter.setBrush(self.brush if not self.isSelected() else QBrush(QColor(255, 180, 90)))
        rect = QRectF(-self._w / 2, -self._h / 2, self._w, self._h)
        painter.drawRect(rect)
        painter.setPen(QPen(QColor(20, 20, 30)))
        painter.drawText(rect, Qt.AlignCenter, self.label)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            sc = self.scene()
            if sc:
                for edge in sc.items():
                    if isinstance(edge, Edge) and (edge.a is self or edge.b is self):
                        edge.update_path()
        return super().itemChange(change, value)


# ----------------------------
# Barnes–Hut QuadTree for repulsion
# ----------------------------
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
        __slots__ = ("cx", "cy", "half", "mass", "com_x", "com_y", "body", "nw", "ne", "sw", "se")

        def __init__(self, cx: float, cy: float, half: float):
            self.cx = cx
            self.cy = cy
            self.half = half
            self.mass = 0.0
            self.com_x = 0.0
            self.com_y = 0.0
            self.body: Optional[Node] = None
            self.nw = self.ne = self.sw = self.se = None

        def is_leaf(self) -> bool:
            return self.nw is None and self.ne is None and self.sw is None and self.se is None

        def _child_for(self, x: float, y: float):
            east = x >= self.cx
            north = y < self.cy
            return (
                ("ne" if east else "nw") if north else ("se" if east else "sw")
            )

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
                if self.body is None:
                    # empty leaf: store body here
                    self.body = node
                    return
                if self.body is node:
                    # same body being re-inserted; nothing to do
                    return
                # Subdivide and reinsert the existing body
                old = self.body
                self.body = None
                quadrant_old = self._child_for(old.pos().x(), old.pos().y())
                self._ensure_child(quadrant_old)
                getattr(self, quadrant_old).insert(old, old.pos().x(), old.pos().y(), 1.0)

            # Insert new body into a child
            quadrant = self._child_for(x, y)
            self._ensure_child(quadrant)
            getattr(self, quadrant).insert(node, x, y, m)

        def compute_force(self, target: Node, tx: float, ty: float, theta: float, k_repulsion: float, eps: float = 0.01) -> Tuple[float, float]:
            if self.mass == 0.0:
                return 0.0, 0.0
            # If this region is just the target itself, ignore
            if self.is_leaf() and self.body is target:
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
        self.k_spring = 0.08       # Hooke spring constant
        self.spring_length = 500.0  # ideal edge length (px)
        self.damping = 0.85        # velocity damping [0..1]
        self.max_step = 30.0       # clamp max displacement per tick
        self.gravity_center = QPointF(0.0, 0.0)
        self.gravity_strength = 0.01  # weak pull to scene center

        # Barnes–Hut parameters
        self.use_barnes_hut = True
        self.bh_theta = 0.7          # smaller = more accurate, slower
        self.bh_min_size = 12        # switch to BH when nodes >= this

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
                    fx, fy = root.compute_force(n, p.x(), p.y(), self.bh_theta, self.k_repulsion, eps=0.01)
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
            a, b = e.a, e.b
            delta = b.pos() - a.pos()
            d = math.hypot(delta.x(), delta.y()) or 0.0001
            force_mag = self.k_spring * (d - self.spring_length) * e.weight
            fx = force_mag * (delta.x() / d)
            fy = force_mag * (delta.y() / d)
            forces[a] += QPointF(fx, fy)
            forces[b] -= QPointF(fx, fy)

        # Weak gravity towards center
        for n in nodes:
            delta = self.gravity_center - n.pos()
            forces[n] += QPointF(delta.x() * self.gravity_strength, delta.y() * self.gravity_strength)

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

class GraphView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(factor, factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake = type("Fake", (), {"button": lambda self: Qt.LeftButton})
            event = type(event)(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        super().mouseReleaseEvent(event)


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.physics = Physics()
        self.timer = QTimer()
        self.timer.setInterval(16)
        self.timer.timeout.connect(self._tick)
        self.running = True
        self.timer.start()

    def _tick(self):
        if not self.running or not self.nodes:
            return
        self.physics.gravity_center = self.sceneRect().center()
        # Only simulate visible items
        vis_nodes = [n for n in self.nodes if n.isVisible()]
        vis_edges = [
            e
            for e in self.edges
            if e.isVisible() and e.a.isVisible() and e.b.isVisible()
        ]
        if vis_nodes:
            self.physics.step(vis_nodes, vis_edges, dt=1.0)
        # Update visible edges' geometry
        for e in vis_edges:
            e.update_path()

    def set_running(self, run: bool):
        self.running = run

    def add_node(
        self,
        label: str,
        pos: Optional[QPointF] = None,
        color: Optional[QColor] = None,
        node_type: str = "generic",
    ) -> Node:
        n = Node(label, color=color, node_type=node_type)
        p = pos if pos is not None else QPointF(random.uniform(-150, 150), random.uniform(-150, 150))
        n.setPos(p)
        self.addItem(n)
        self.nodes.append(n)
        return n

    def add_edge(
        self, a: Node, b: Node, weight: float = 1.0, edge_type: str = "generic"
    ) -> Edge:
        e = Edge(a, b, weight, edge_type=edge_type)
        self.addItem(e)
        self.edges.append(e)
        return e

    def clear_graph(self):
        for e in self.edges:
            self.removeItem(e)
        for n in self.nodes:
            self.removeItem(n)
        self.nodes.clear()
        self.edges.clear()

    def auto_scene_rect(self):
        # Fit to visible nodes if any
        vis = [n for n in self.nodes if n.isVisible()]
        items = vis if vis else self.nodes
        if not items:
            self.setSceneRect(QRectF(-200, -200, 400, 400))
            return
        xs = [n.pos().x() for n in items]
        ys = [n.pos().y() for n in items]
        minx, maxx = min(xs) - 120, max(xs) + 120
        miny, maxy = min(ys) - 120, max(ys) + 120
        self.setSceneRect(QRectF(minx, miny, maxx - minx, maxy - miny))

    # Apply visibility filters for nodes and edges
    def apply_filters(self, node_flags: Dict[str, bool], edge_flags: Dict[str, bool]):
        for n in self.nodes:
            show = node_flags.get(n.node_type, True)
            n.setVisible(show)
        for e in self.edges:
            show_edge = edge_flags.get(e.edge_type, True)
            show_edge = show_edge and e.a.isVisible() and e.b.isVisible()
            e.setVisible(show_edge)
        # Update scene rect after visibility changes
        self.auto_scene_rect()


class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Force‑Directed Graph — PySide6 (Barnes–Hut)")
        self.scene = GraphScene()
        self.view = GraphView(self.scene)
        self.setCentralWidget(self.view)
        self._build_toolbar()
        self._populate_demo()
        self.scene.auto_scene_rect()
        self.resize(1000, 700)

    def _build_toolbar(self):
        tb = QToolBar("Controls")
        tb.setMovable(False)
        self.addToolBar(tb)

        # Play/Pause
        self.btn_play = QToolButton()
        self.btn_play.setText("Pause")
        self.btn_play.clicked.connect(self._toggle_running)
        tb.addWidget(self.btn_play)

        # Re-center
        btn_center = QToolButton()
        btn_center.setText("Center")
        btn_center.clicked.connect(self._center_view)
        tb.addWidget(btn_center)

        # Random graph
        btn_random = QToolButton()
        btn_random.setText("Random Graph")
        btn_random.clicked.connect(self._populate_demo)
        tb.addWidget(btn_random)

        # Clear
        btn_clear = QToolButton()
        btn_clear.setText("Clear")
        btn_clear.clicked.connect(self._clear)
        tb.addWidget(btn_clear)

        # Load bSDD JSON
        btn_load = QToolButton()
        btn_load.setText("Load bSDD JSON")
        btn_load.clicked.connect(self._load_bsdd_json)
        tb.addWidget(btn_load)

        tb.addSeparator()

        # Spring length slider
        tb.addWidget(QLabel("L₀:"))
        self.spring_slider = QSlider(Qt.Horizontal)
        self.spring_slider.setRange(30, 200)
        self.spring_slider.setValue(int(self.scene.physics.spring_length))
        self.spring_slider.valueChanged.connect(lambda v: setattr(self.scene.physics, "spring_length", float(v)))
        tb.addWidget(self.spring_slider)

        tb.addWidget(QLabel("k_spring:"))
        self.k_slider = QSlider(Qt.Horizontal)
        self.k_slider.setRange(1, 200)
        self.k_slider.setValue(int(self.scene.physics.k_spring * 100))
        self.k_slider.valueChanged.connect(lambda v: setattr(self.scene.physics, "k_spring", float(v) / 100.0))
        tb.addWidget(self.k_slider)

        tb.addWidget(QLabel("repulse:"))
        self.repulse_slider = QSlider(Qt.Horizontal)
        self.repulse_slider.setRange(100, 5000)
        self.repulse_slider.setValue(int(self.scene.physics.k_repulsion))
        self.repulse_slider.valueChanged.connect(lambda v: setattr(self.scene.physics, "k_repulsion", float(v)))
        tb.addWidget(self.repulse_slider)

        tb.addSeparator()

        # Node toggles
        tb.addWidget(QLabel("Nodes:"))
        self.tg_nodes_class = QToolButton()
        self.tg_nodes_class.setText("Classes")
        self.tg_nodes_class.setCheckable(True)
        self.tg_nodes_class.setChecked(True)
        self.tg_nodes_class.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_nodes_class)

        self.tg_nodes_classprop = QToolButton()
        self.tg_nodes_classprop.setText("ClassProps")
        self.tg_nodes_classprop.setCheckable(True)
        self.tg_nodes_classprop.setChecked(False)
        self.tg_nodes_classprop.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_nodes_classprop)

        self.tg_nodes_prop = QToolButton()
        self.tg_nodes_prop.setText("Properties")
        self.tg_nodes_prop.setCheckable(True)
        self.tg_nodes_prop.setChecked(True)
        self.tg_nodes_prop.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_nodes_prop)

        tb.addSeparator()

        # Edge toggles
        tb.addWidget(QLabel("Edges:"))
        self.tg_edge_class_rel = QToolButton()
        self.tg_edge_class_rel.setText("Class↔Class")
        self.tg_edge_class_rel.setCheckable(True)
        self.tg_edge_class_rel.setChecked(False)
        self.tg_edge_class_rel.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_class_rel)

        self.tg_edge_prop_rel = QToolButton()
        self.tg_edge_prop_rel.setText("Prop↔Prop")
        self.tg_edge_prop_rel.setCheckable(True)
        self.tg_edge_prop_rel.setChecked(False)
        self.tg_edge_prop_rel.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_prop_rel)

        self.tg_edge_class_to_cp = QToolButton()
        self.tg_edge_class_to_cp.setText("Class→CP")
        self.tg_edge_class_to_cp.setCheckable(True)
        self.tg_edge_class_to_cp.setChecked(False)
        self.tg_edge_class_to_cp.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_class_to_cp)

        self.tg_edge_cp_to_prop = QToolButton()
        self.tg_edge_cp_to_prop.setText("CP→Prop")
        self.tg_edge_cp_to_prop.setCheckable(True)
        self.tg_edge_cp_to_prop.setChecked(False)
        self.tg_edge_cp_to_prop.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_cp_to_prop)

        self.tg_edge_cl_to_prop = QToolButton()
        self.tg_edge_cl_to_prop.setText("Class→Prop")
        self.tg_edge_cl_to_prop.setCheckable(True)
        self.tg_edge_cl_to_prop.setChecked(True)
        self.tg_edge_cl_to_prop.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_cl_to_prop)

    # ---- Actions ----
    def _toggle_running(self):
        self.scene.set_running(not self.scene.running)
        self.btn_play.setText("Pause" if self.scene.running else "Play")
        # print(f"[DEBUG] GraphWindow._toggle_running: now running={self.scene.running}")

    def _center_view(self):
        self.scene.auto_scene_rect()
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        # print("[DEBUG] GraphWindow._center_view: view centered on scene rect")

    def _clear(self):
        self.scene.clear_graph()
        # print("[DEBUG] GraphWindow._clear: scene cleared")

    def _populate_demo(self):
        # Build a small random-ish graph (Erdos–Renyi style)
        # print("[DEBUG] GraphWindow._populate_demo: building demo graph")
        self.scene.clear_graph()
        random.seed()
        colors = [QColor(80, 140, 255), QColor(140, 200, 90), QColor(250, 150, 90), QColor(200, 120, 220)]
        N = 18
        nodes = [
            self.scene.add_node(str(i), color=random.choice(colors), node_type="demo")
            for i in range(N)
        ]
        # connect with probability p
        p = 0.13
        for i in range(N):
            for j in range(i + 1, N):
                if random.random() < p:
                    self.scene.add_edge(
                        nodes[i], nodes[j], weight=1.0, edge_type="demo"
                    )
        # Ensure connectivity roughly: connect each node to a previous one
        for i in range(1, N):
            self.scene.add_edge(nodes[i - 1], nodes[i], weight=1.0, edge_type="demo")
        self.scene.auto_scene_rect()
        # print(f"[DEBUG] GraphWindow._populate_demo: demo graph built with {len(nodes)} nodes and {len(self.scene.edges)} edges")

    # ---- bSDD integration ----
    def _load_bsdd_json(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open bSDD JSON",
            "",
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            # print("[DEBUG] GraphWindow._load_bsdd_json: canceled by user")
            return
        try:
            bsdd_dict = BsddDictionary.load(path)
        except Exception as e:
            # print(f"[DEBUG] GraphWindow._load_bsdd_json: failed to load '{path}': {e}")
            return
            # print(
            f"[DEBUG] GraphWindow._load_bsdd_json: loaded dictionary '{bsdd_dict.DictionaryName or bsdd_dict.DictionaryCode}' with {len(bsdd_dict.Classes)} classes"
        # )
        self._populate_from_bsdd(bsdd_dict)

    def _populate_from_bsdd(self, bsdd_dict: BsddDictionary):
        # Build graph from bSDD model: Classes (red), ClassProperties (green), Properties (blue)
        self.scene.clear_graph()

        CLASS_COLOR = QColor(220, 60, 60)  # red
        CLPROP_COLOR = QColor(60, 170, 60)  # green
        PROP_COLOR = QColor(60, 120, 220)  # blue

        # Node registries
        class_by_code: Dict[str, Node] = {}
        class_by_uri: Dict[str, Node] = {}
        prop_by_code: Dict[str, Node] = {}
        prop_by_uri: Dict[str, Node] = {}
        classprop_nodes: List[Tuple[BsddClassProperty, Node]] = []

        # 1) Classes
        for c in bsdd_dict.Classes:
            n = self.scene.add_node(
                c.Code or c.Name or "Class", color=CLASS_COLOR, node_type="class"
            )
            class_by_code[c.Code] = n
            try:
                uri = cl_utils.build_bsdd_uri(c, bsdd_dict)
                if uri:
                    class_by_uri[uri] = n
            except Exception:
                pass

        # 2) Properties (dictionary-level)
        for p in bsdd_dict.Properties:
            n = self.scene.add_node(
                p.Code or p.Name or "Property", color=PROP_COLOR, node_type="property"
            )
            prop_by_code[p.Code] = n
            # Map canonical bsDD URI and any owned URI
            try:
                uri = prop_utils.build_bsdd_uri(p, bsdd_dict)
                if uri:
                    prop_by_uri[uri] = n
            except Exception:
                pass
            if getattr(p, "OwnedUri", None):
                prop_by_uri[p.OwnedUri] = n

        # 3) ClassProperties and edges: Class -> ClassProperty
        for c in bsdd_dict.Classes:
            cnode = class_by_code.get(c.Code)
            if not cnode:
                continue
            for cp in c.ClassProperties:
                label = cp.Code or cp.PropertyCode or "ClassProperty"
                cp_node = self.scene.add_node(
                    label, color=CLPROP_COLOR, node_type="classprop"
                )
                self.scene.add_edge(
                    cnode, cp_node, weight=1.0, edge_type="class_to_classprop"
                )
                classprop_nodes.append((cp, cp_node))

        # 4) ClassRelations edges (Class -> Class)
        for c in bsdd_dict.Classes:
            src_node = class_by_code.get(c.Code)
            if not src_node:
                continue
            for rel in c.ClassRelations:
                # dst_node = class_by_uri.get(rel.RelatedClassUri)
                dst_node = class_by_code.get(c.ParentClassCode)
                if dst_node is not None:
                    self.scene.add_edge(
                        src_node, dst_node, weight=1.0, edge_type="class_rel"
                    )

        # 5) PropertyRelations edges (Property -> Property)
        for p in bsdd_dict.Properties:
            src_node = prop_by_code.get(p.Code)
            if not src_node:
                continue
            for rel in p.PropertyRelations:
                dst = prop_by_uri.get(rel.RelatedPropertyUri)
                if dst is None:
                    # Fallback: parse URI to code
                    try:
                        parsed = dict_utils.parse_bsdd_url(rel.RelatedPropertyUri)
                        code = parsed.get("resource_id")
                        if code and code in prop_by_code:
                            dst = prop_by_code[code]
                    except Exception:
                        pass
                if dst is not None:
                    self.scene.add_edge(src_node, dst, weight=1.0, edge_type="prop_rel")

        # 6) Edges ClassProperty -> Property (link class property to its property)
        for cp, cp_node in classprop_nodes:
            parent_class = cp._parent_ref()
            class_node = class_by_code(parent_class.Code)
            target_node = None
            # Prefer PropertyUri mapping
            if getattr(cp, "PropertyUri", None):
                target_node = prop_by_uri.get(cp.PropertyUri)
                if target_node is None:
                    # try parse to code
                    try:
                        parsed = dict_utils.parse_bsdd_url(cp.PropertyUri)
                        code = parsed.get("resource_id")
                        if code:
                            target_node = prop_by_code.get(code)
                    except Exception:
                        pass
            # Fallback to PropertyCode
            if target_node is None and getattr(cp, "PropertyCode", None):
                target_node = prop_by_code.get(cp.PropertyCode)
            if target_node is not None:
                self.scene.add_edge(
                    cp_node, target_node, weight=1.0, edge_type="classprop_to_prop"
                )
                self.scene.add_edge(
                    cp_node, class_node, weight=1.0, edge_type="class_to_prop"
                )

        # Apply current filters to the newly created graph
        self._apply_filters()

    def _apply_filters(self):
        node_flags = {
            "class": (
                self.tg_nodes_class.isChecked()
                if hasattr(self, "tg_nodes_class")
                else True
            ),
            "classprop": (
                self.tg_nodes_classprop.isChecked()
                if hasattr(self, "tg_nodes_classprop")
                else True
            ),
            "property": (
                self.tg_nodes_prop.isChecked()
                if hasattr(self, "tg_nodes_prop")
                else True
            ),
        }
        edge_flags = {
            "class_rel": (
                self.tg_edge_class_rel.isChecked()
                if hasattr(self, "tg_edge_class_rel")
                else True
            ),
            "prop_rel": (
                self.tg_edge_prop_rel.isChecked()
                if hasattr(self, "tg_edge_prop_rel")
                else True
            ),
            "class_to_classprop": (
                self.tg_edge_class_to_cp.isChecked()
                if hasattr(self, "tg_edge_class_to_cp")
                else True
            ),
            "classprop_to_prop": (
                self.tg_edge_cp_to_prop.isChecked()
                if hasattr(self, "tg_edge_cp_to_prop")
                else True
            ),
            "class_to_prop": (
                self.tg_edge_cl_to_prop.isChecked()
                if hasattr(self, "tg_edge_cl_to_prop")
                else True
            ),
            # default types (e.g., demo) remain visible by default
        }
        # Apply to scene
        self.scene.apply_filters(node_flags, edge_flags)

        self.scene.auto_scene_rect()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = GraphWindow()
    w.show()
    sys.exit(app.exec())
