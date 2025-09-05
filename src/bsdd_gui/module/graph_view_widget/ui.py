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
    QFileDialog,
)

from bsdd_gui.module.graph_view_widget.view import GraphScene, GraphView
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bsdd_gui.module.graph_view_widget.graphics_items import Node, Edge


class GraphWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Force‑Directed Graph — PySide6 (Barnes–Hut)")
        self.scene = GraphScene()
        self.view = GraphView(self.scene)
        self.setCentralWidget(self.view)
        self._build_toolbar()
        # self._populate_demo()
        self.bsdd_dict = BsddDictionary.load(
            r"/home/christoph/Github/bSDD-Toolkit/test_bsdd_reduced_v2.json"
        )
        self._populate_from_bsdd(self.bsdd_dict)
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
        self.spring_slider.setRange(100, 1000)
        self.spring_slider.setValue(int(self.scene.physics.spring_length))
        self.spring_slider.valueChanged.connect(
            lambda v: setattr(self.scene.physics, "spring_length", float(v))
        )
        tb.addWidget(self.spring_slider)

        tb.addWidget(QLabel("k_spring:"))
        self.k_slider = QSlider(Qt.Horizontal)
        self.k_slider.setRange(0.01, 10)
        self.k_slider.setValue(int(self.scene.physics.k_spring * 100))
        self.k_slider.valueChanged.connect(
            lambda v: setattr(self.scene.physics, "k_spring", float(v) / 100.0)
        )
        tb.addWidget(self.k_slider)

        tb.addWidget(QLabel("repulse:"))
        self.repulse_slider = QSlider(Qt.Horizontal)
        self.repulse_slider.setRange(100, 5000)
        self.repulse_slider.setValue(int(self.scene.physics.k_repulsion))
        self.repulse_slider.valueChanged.connect(
            lambda v: setattr(self.scene.physics, "k_repulsion", float(v))
        )
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
        self.tg_edge_class_rel.setChecked(True)
        self.tg_edge_class_rel.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_class_rel)

        self.tg_edge_prop_rel = QToolButton()
        self.tg_edge_prop_rel.setText("Prop↔Prop")
        self.tg_edge_prop_rel.setCheckable(True)
        self.tg_edge_prop_rel.setChecked(True)
        self.tg_edge_prop_rel.clicked.connect(self._apply_filters)
        tb.addWidget(self.tg_edge_prop_rel)

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
        colors = [
            QColor(80, 140, 255),
            QColor(140, 200, 90),
            QColor(250, 150, 90),
            QColor(200, 120, 220),
        ]
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
                    self.scene.add_edge(nodes[i], nodes[j], weight=1.0, edge_type="demo")
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
        # Build graph from bSDD model: Classes and Properties
        self.scene.clear_graph()

        # Node registries
        class_by_code: Dict[str, Node] = {}
        class_by_uri: Dict[str, Node] = {}
        prop_by_code: Dict[str, Node] = {}
        prop_by_uri: Dict[str, Node] = {}

        # 1) Classes
        for c in bsdd_dict.Classes:
            n = self.scene.add_node(c.Code or c.Name or "Class", node_type="class")
            class_by_code[c.Code] = n
            try:
                uri = cl_utils.build_bsdd_uri(c, bsdd_dict)
                if uri:
                    class_by_uri[uri] = n
            except Exception:
                pass

        # 2) Properties (dictionary-level)
        for p in bsdd_dict.Properties:
            n = self.scene.add_node(p.Code or p.Name or "Property", node_type="property")
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

        # 3) Class → Property edges via ClassProperties
        for c in bsdd_dict.Classes:
            cnode = class_by_code.get(c.Code)
            if not cnode:
                continue
            for cp in c.ClassProperties:
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
                    self.scene.add_edge(cnode, target_node, weight=1.0, edge_type="class_to_prop")

        # 4) ClassRelations edges (Class -> Class)
        for c in bsdd_dict.Classes:
            src_node = class_by_code.get(c.Code)
            if not src_node:
                continue
            dst_node = class_by_code.get(c.ParentClassCode)
            if not dst_node:
                continue
            self.scene.add_edge(src_node, dst_node, weight=1.0, edge_type="class_rel")
            # for rel in c.ClassRelations:
            #     dst_node = class_by_uri.get(rel.RelatedClassUri)
            #     if dst_node is not None:
            #         self.scene.add_edge(
            #             src_node, dst_node, weight=1.0, edge_type="class_rel"
            #         )

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
                    self.scene.add_edge(src_node, dst, weight=0.0, edge_type="prop_rel")

        # No ClassProperty nodes are created; edges Class→Property were added above.

        # Apply current filters to the newly created graph
        self._apply_filters()

    def _apply_filters(self):
        node_flags = {
            "class": (self.tg_nodes_class.isChecked() if hasattr(self, "tg_nodes_class") else True),
            "property": (
                self.tg_nodes_prop.isChecked() if hasattr(self, "tg_nodes_prop") else True
            ),
        }
        edge_flags = {
            "class_rel": (
                self.tg_edge_class_rel.isChecked() if hasattr(self, "tg_edge_class_rel") else True
            ),
            "prop_rel": (
                self.tg_edge_prop_rel.isChecked() if hasattr(self, "tg_edge_prop_rel") else True
            ),
            "class_to_prop": (
                self.tg_edge_cl_to_prop.isChecked() if hasattr(self, "tg_edge_cl_to_prop") else True
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
