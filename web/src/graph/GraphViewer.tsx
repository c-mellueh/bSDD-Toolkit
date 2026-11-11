/* eslint-disable @typescript-eslint/no-explicit-any */
import { Accordion, ActionIcon, Autocomplete, Badge, Button, Divider, FileButton, Group, Menu, Modal, SegmentedControl, Select, Slider, Stack, Switch, Text, Tooltip, useComputedColorScheme } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { Toggle } from "../components/Toggle";
import {
  IconArrowsMaximize,
  IconBooks,
  IconChevronDown,
  IconChevronLeft,
  IconChevronRight,
  IconChevronUp,
  IconDownload,
  IconEraser,
  IconExternalLink,
  IconHelp,
  IconLayoutGrid,
  IconPlayerPause,
  IconPlayerPlay,
  IconPlus,
  IconRefresh,
  IconTrash,
  IconZoomIn,
  IconZoomOut,
} from "@tabler/icons-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { saveBlob } from "../api";
import { divider, useContextMenu, type MenuItem } from "../components/ContextMenu";
import { askConfirm } from "../components/dialogs";
import { CLASS_RELATION_TYPES, GOP, MATERIAL, PROPERTY_RELATION_TYPES } from "../model";
import { attempt, notifyError } from "../notify";
import { op, useProject } from "../state/project";
import { storageGet, storageSet } from "../state/settings";
import { openUi } from "../state/ui";
import { GraphLibrary } from "./GraphLibrary";
import { buildTab, htmlPage, rootClassTabs } from "./htmlExport";
import { hasGraphDrag, readGraphDrag } from "./dnd";
import { circleLayout, gridLayout, normalizeTreeOrder, packComponents, TREE_EDGE_KINDS, treeLayout } from "./layout";
import {
  EDGE_KINDS,
  edgeKindLabel,
  EDGE_STYLE,
  NODE_KINDS,
  NODE_STYLE,
  classId,
  describeNode,
  edgesBetween,
  externalLabels,
  neighbours,
  propId,
  resolveInput,
  type EdgeKind,
  type GEdge,
  type GNode,
  type NodeKind,
} from "./model";
import { bounds, draw, hitEdge, hitNode, nodeSize, redgesFrom, toSvg, type DrawOptions, type REdge, type RNode, type Routing, type View } from "./renderer";
import wasmUrl from "./engine.wasm?url";

interface Physics {
  repulsion: number;
  springLength: number;
  springK: number;
  gravity: number;
  damping: number;
  theta: number;
  maxSpeed: number;
  collision: number;
}

const DEFAULT_PHYSICS: Physics = { repulsion: 1200, springLength: 90, springK: 0.04, gravity: 0.02, damping: 0.6, theta: 0.8, maxSpeed: 60, collision: 1 };

interface Appearance {
  routing: Routing;
  labels: boolean;
  edgeLabels: boolean;
  arrows: boolean;
  pinOnDrag: boolean;
  physicsOnDrag: boolean;
}

const DEFAULT_APPEARANCE: Appearance = { routing: "straight", labels: true, edgeLabels: false, arrows: true, pinOnDrag: true, physicsOnDrag: true };

const LIBRARY_WIDTH_KEY = "bsdd-graph-library-width";
const LIBRARY_DEFAULT = 260;
const LIBRARY_MIN = 180;
const LIBRARY_MAX = 700;
const clampLibrary = (w: number) => Math.round(Math.max(LIBRARY_MIN, Math.min(LIBRARY_MAX, Math.min(window.innerWidth * 0.6, Number(w) || LIBRARY_DEFAULT))));

interface Saved {
  scene: string[];
  pos: Record<string, [number, number, number]>; // x, y, fixed
  hiddenNodes: NodeKind[];
  hiddenEdges: EdgeKind[];
  /** edge kinds in the order the tree layout uses them */
  treeOrder: EdgeKind[];
  physics: Physics;
  appearance: Appearance;
  library: boolean;
}

type Drag =
  | { type: "nodes"; items: { i: number; dx: number; dy: number }[]; moved: boolean }
  | { type: "pan"; sx: number; sy: number; vx: number; vy: number }
  | { type: "box"; x1: number; y1: number; x2: number; y2: number; add: boolean }
  | { type: "connect"; from: number; x: number; y: number }
  | null;

export function GraphViewer({ projectId, standalone }: { projectId: string; standalone?: boolean }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const activeClass = useProject((s) => s.activeClass);
  const selectedClasses = useProject((s) => s.selectedClasses);
  const dark = useComputedColorScheme("light") === "dark";
  const openMenu = useContextMenu((s) => s.open);
  const storeKey = `bsdd-graph-${projectId}`;

  const saved = useMemo(() => storageGet<Partial<Saved>>(storeKey, {}), [storeKey]);
  const [scene, setScene] = useState<string[]>(saved.scene ?? []);
  const [hiddenNodes, setHiddenNodes] = useState<Set<NodeKind>>(new Set(saved.hiddenNodes ?? []));
  const [hiddenEdges, setHiddenEdges] = useState<Set<EdgeKind>>(new Set(saved.hiddenEdges ?? []));
  const [treeOrder, setTreeOrder] = useState<EdgeKind[]>(normalizeTreeOrder(saved.treeOrder));
  const [physics, setPhysics] = useState<Physics>({ ...DEFAULT_PHYSICS, ...(saved.physics ?? {}) });
  const [appearance, setAppearance] = useState<Appearance>({ ...DEFAULT_APPEARANCE, ...(saved.appearance ?? {}) });
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [selectedEdge, setSelectedEdge] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [ready, setReady] = useState(false);
  const [panel, setPanel] = useState(true);
  const [library, setLibrary] = useState<boolean>(saved.library ?? true);
  // width of the dictionary panel (per browser, all projects)
  const [libraryWidth, setLibraryWidth] = useState<number>(() => clampLibrary(storageGet(LIBRARY_WIDTH_KEY, LIBRARY_DEFAULT)));
  const libraryDrag = useRef<{ start: number; initial: number } | null>(null);
  const resizeLibrary = (w: number) => {
    const v = clampLibrary(w);
    setLibraryWidth(v);
    storageSet(LIBRARY_WIDTH_KEY, v);
  };
  useEffect(() => {
    const move = (e: PointerEvent) => {
      if (libraryDrag.current) setLibraryWidth(clampLibrary(libraryDrag.current.initial + e.clientX - libraryDrag.current.start));
    };
    const up = (e: PointerEvent) => {
      if (!libraryDrag.current) return;
      resizeLibrary(libraryDrag.current.initial + e.clientX - libraryDrag.current.start);
      libraryDrag.current = null;
      document.body.classList.remove("resizing");
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  // phones: the side panels would leave no room for the graph – start closed, open as overlays
  const narrow = useMediaQuery("(max-width: 48em)") ?? false;
  useEffect(() => {
    if (narrow) {
      setPanel(false);
      setLibrary(false);
    }
  }, [narrow]);
  const overlay = (side: "left" | "right"): React.CSSProperties =>
    narrow
      ? { position: "absolute", top: 0, bottom: 0, [side]: 0, zIndex: 5, width: "min(86vw, 320px)", background: "var(--mantine-color-body)", boxShadow: "var(--mantine-shadow-lg)" }
      : {};
  const [dropActive, setDropActive] = useState(false);
  const [input, setInput] = useState("");
  const [connect, setConnect] = useState<{ source: string; target: string } | null>(null);
  const [connectMode, setConnectMode] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const worker = useRef<Worker | null>(null);
  const pos = useRef(new Map<string, { x: number; y: number; fixed: boolean }>(Object.entries(saved.pos ?? {}).map(([k, v]) => [k, { x: v[0], y: v[1], fixed: !!v[2] }])));
  const rnodes = useRef<RNode[]>([]);
  const redges = useRef<REdge[]>([]);
  const view = useRef<View>({ x: 0, y: 0, k: 1 });
  const size = useRef({ w: 0, h: 0, dpr: 1 });
  const drag = useRef<Drag>(null);
  const hover = useRef<number | null>(null);
  const dirty = useRef(true);
  const frame = useRef<number>();
  const fitPending = useRef(true);
  const initialised = useRef(false);
  const pendingAlpha = useRef<number | undefined>(undefined);
  /** nodes added since the graph was last sent to the physics worker */
  const pendingNew = useRef(new Set<string>());
  /** physics in play mode (not paused) */
  const playing = useRef(false);
  /** nodes of the current settle run (the only ones that may move while paused) */
  const settling = useRef(new Set<string>());

  // ------------------------------------------------------------------ derived graph

  const labels = useMemo(() => (doc ? externalLabels(doc) : new Map<string, string>()), [doc]);

  const graph = useMemo(() => {
    if (!doc) return { nodes: [] as (GNode & { w: number; h: number; display: string })[], edges: [] as GEdge[], all: [] as GNode[], allEdges: [] as GEdge[] };
    const all: GNode[] = [];
    for (const id of scene) {
      const n = describeNode(doc, idx, id, labels);
      if (n) all.push(n);
    }
    const allIds = new Set(all.map((n) => n.id));
    const allEdges = edgesBetween(doc, idx, allIds);
    const nodes = all
      .filter((n) => !hiddenNodes.has(n.kind))
      .map((n) => {
        const s = nodeSize(n.label, n.kind);
        return { ...n, w: s.w, h: s.h, display: s.label };
      });
    const visibleIds = new Set(nodes.map((n) => n.id));
    const edges = allEdges.filter((e) => !hiddenEdges.has(e.kind) && visibleIds.has(e.source) && visibleIds.has(e.target));
    return { nodes, edges, all, allEdges };
  }, [doc, idx, scene, hiddenNodes, hiddenEdges, labels]);

  const indexOf = useMemo(() => new Map(graph.nodes.map((n, i) => [n.id, i])), [graph.nodes]);
  const adjacency = useMemo(() => {
    const adj = new Map<number, Set<number>>();
    for (const e of redgesFrom(graph.edges, indexOf)) {
      if (!adj.has(e.s)) adj.set(e.s, new Set());
      if (!adj.has(e.t)) adj.set(e.t, new Set());
      adj.get(e.s)!.add(e.t);
      adj.get(e.t)!.add(e.s);
    }
    return adj;
  }, [graph.edges, indexOf]);

  const requestDraw = useCallback(() => {
    dirty.current = true;
    if (frame.current === undefined) frame.current = requestAnimationFrame(render);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // initial scene (nothing saved yet): small dictionaries completely; larger ones only the root
  // classes and their direct children (no Groups of Properties – their many HasReference edges
  // make an unreadable tangle), laid out as a tree instead of starting from random positions
  const initialLayout = useRef(false);
  const treeOrderRef = useRef(treeOrder);
  treeOrderRef.current = treeOrder;
  useEffect(() => {
    if (initialised.current || !doc) return;
    initialised.current = true;
    if (scene.length) return;
    const classes = doc.dictionary.Classes ?? [];
    if (classes.length <= 60) {
      setScene(classes.map((c) => classId(c.Code)));
      return;
    }
    const main = classes.filter((c) => c.ClassType !== GOP && c.ClassType !== MATERIAL);
    const codes = new Set(main.map((c) => c.Code));
    const roots = new Set(main.filter((c) => !c.ParentClassCode || !codes.has(c.ParentClassCode)).map((c) => c.Code));
    const top = main.filter((c) => roots.has(c.Code) || roots.has(c.ParentClassCode ?? ""));
    setScene((top.length ? top : main.slice(0, 60)).map((c) => classId(c.Code)));
    initialLayout.current = true;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doc]);

  // build render arrays + send the graph to the physics worker
  useEffect(() => {
    const nodes = graph.nodes;
    const placed = new Map<string, { x: number; y: number }>();
    for (const n of nodes) {
      const p = pos.current.get(n.id);
      if (p) placed.set(n.id, p);
    }
    // place new nodes next to an already placed neighbour
    const neighbourOf = new Map<string, string[]>();
    for (const e of graph.edges) {
      if (!neighbourOf.has(e.source)) neighbourOf.set(e.source, []);
      if (!neighbourOf.has(e.target)) neighbourOf.set(e.target, []);
      neighbourOf.get(e.source)!.push(e.target);
      neighbourOf.get(e.target)!.push(e.source);
    }
    let cx = 0;
    let cy = 0;
    if (placed.size) {
      for (const p of placed.values()) {
        cx += p.x;
        cy += p.y;
      }
      cx /= placed.size;
      cy /= placed.size;
    }
    let newCount = 0;
    for (const n of nodes) {
      if (placed.has(n.id)) continue;
      pendingNew.current.add(n.id);
      const anchor = (neighbourOf.get(n.id) ?? []).map((id) => placed.get(id)).find(Boolean);
      const a = Math.random() * Math.PI * 2;
      const r = anchor ? 60 + Math.random() * 60 : 40 + Math.sqrt(nodes.length) * 20 * Math.random();
      const p = { x: (anchor?.x ?? cx) + Math.cos(a) * r, y: (anchor?.y ?? cy) + Math.sin(a) * r, fixed: false };
      placed.set(n.id, p);
      pos.current.set(n.id, p);
      newCount++;
    }
    rnodes.current = nodes.map((n) => {
      const p = pos.current.get(n.id)!;
      return { id: n.id, kind: n.kind, label: n.display, x: p.x, y: p.y, w: n.w, h: n.h, fixed: p.fixed };
    });
    redges.current = redgesFrom(graph.edges, indexOf);
    if (initialLayout.current && nodes.length) {
      // first opening of a larger dictionary: tidy tree, no physics run
      initialLayout.current = false;
      const lnodes = rnodes.current.map((n) => ({ id: n.id, w: n.w, h: n.h }));
      const aspect = size.current.w && size.current.h ? size.current.w / size.current.h : 1.4;
      const result = packComponents(treeLayout(lnodes, graph.edges, "LR", treeOrderRef.current), lnodes, graph.edges, aspect);
      for (const n of rnodes.current) {
        const p = result.get(n.id);
        if (!p) continue;
        n.x = p.x;
        n.y = p.y;
        const stored = pos.current.get(n.id);
        if (stored) {
          stored.x = p.x;
          stored.y = p.y;
        }
      }
      newCount = 0;
      pendingNew.current.clear();
      fitPending.current = true;
    }
    if (newCount > 0) pendingAlpha.current = Math.max(pendingAlpha.current ?? 0, newCount === nodes.length ? 1 : 0.5);
    if (worker.current && ready) {
      sendGraph(pendingAlpha.current);
      pendingAlpha.current = undefined;
      pendingNew.current.clear();
    }
    requestDraw();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph, indexOf, ready]);

  const sendGraph = (alpha?: number) => {
    const nodes = rnodes.current;
    const edges = redges.current;
    const n = nodes.length;
    const m = edges.length;
    const positions = new Float32Array(n * 2);
    const fixed = new Uint8Array(n);
    const mass = new Float32Array(n);
    const radius = new Float32Array(n);
    const degree = new Uint32Array(n);
    for (const e of edges) {
      degree[e.s]++;
      degree[e.t]++;
    }
    nodes.forEach((nd, i) => {
      positions[2 * i] = nd.x;
      positions[2 * i + 1] = nd.y;
      fixed[i] = nd.fixed ? 1 : 0;
      mass[i] = 1 + Math.min(degree[i], 20) * 0.1;
      radius[i] = Math.max(nd.w, nd.h) / 2 + 4;
    });
    const edgeArr = new Uint32Array(m * 2);
    const rest = new Float32Array(m);
    const strength = new Float32Array(m);
    edges.forEach((e, k) => {
      edgeArr[2 * k] = e.s;
      edgeArr[2 * k + 1] = e.t;
      rest[k] = e.kind === "ClassProperty" || e.kind === "GopProperty" ? 0.7 : 1;
      strength[k] = e.kind === "ParentClassCode" ? 1.5 : 1 / Math.max(1, Math.min(degree[e.s], degree[e.t]) * 0.5);
    });
    // paused: only the new nodes settle, the others keep their place
    // (also while an earlier settle run is still going)
    let moveOnly: number[] | undefined;
    if (!playing.current && (alpha !== undefined || settling.current.size)) {
      for (const id of pendingNew.current) settling.current.add(id);
      moveOnly = nodes.flatMap((nd, i) => (settling.current.has(nd.id) ? [i] : []));
    }
    worker.current!.postMessage({ type: "graph", n, m, positions, fixed, mass, radius, edges: edgeArr, rest, strength, alpha, moveOnly }, [positions.buffer, fixed.buffer, mass.buffer, radius.buffer, edgeArr.buffer, rest.buffer, strength.buffer]);
  };

  // ------------------------------------------------------------------ worker

  useEffect(() => {
    const w = new Worker(new URL("./physics.worker.ts", import.meta.url), { type: "module" });
    worker.current = w;
    w.onmessage = (ev) => {
      const m = ev.data;
      if (m.type === "ready") {
        w.postMessage({ type: "params", params: physics });
        setReady(true);
      } else if (m.type === "positions") {
        const p: Float32Array = m.positions;
        const nodes = rnodes.current;
        const dragging = drag.current?.type === "nodes" ? new Set(drag.current.items.map((x) => x.i)) : null;
        for (let i = 0; i < nodes.length && 2 * i + 1 < p.length; i++) {
          if (dragging?.has(i)) continue;
          nodes[i].x = p[2 * i];
          nodes[i].y = p[2 * i + 1];
          const stored = pos.current.get(nodes[i].id);
          if (stored) {
            stored.x = nodes[i].x;
            stored.y = nodes[i].y;
          }
        }
        setRunning(m.running);
        playing.current = !!m.continuous;
        if (!m.running || playing.current) settling.current.clear();
        if (fitPending.current) {
          fit();
          if (m.running) fitPending.current = true;
        }
        requestDraw();
      }
    };
    w.postMessage({ type: "init", wasmUrl });
    return () => w.terminate();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    worker.current?.postMessage({ type: "params", params: physics, reheat: true });
  }, [physics]);

  // ------------------------------------------------------------------ persistence

  const saveRef = useRef<() => void>(() => undefined);
  useEffect(() => {
    const id = window.setInterval(() => saveRef.current(), 3000);
    return () => {
      window.clearInterval(id);
      saveRef.current();
    };
  }, []);
  const save = () => {
    const keep = new Set(scene);
    const p: Saved["pos"] = {};
    for (const [k, v] of pos.current) if (keep.has(k)) p[k] = [Math.round(v.x), Math.round(v.y), v.fixed ? 1 : 0];
    storageSet(storeKey, { scene, pos: p, hiddenNodes: [...hiddenNodes], hiddenEdges: [...hiddenEdges], treeOrder, physics, appearance, library } satisfies Saved);
  };
  saveRef.current = save;

  useEffect(requestDraw, [appearance, dark, selected, selectedEdge, requestDraw]);

  // ------------------------------------------------------------------ canvas sizing + drawing

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver(() => {
      const dpr = window.devicePixelRatio || 1;
      const w = el.clientWidth;
      const h = el.clientHeight;
      size.current = { w, h, dpr };
      const c = canvasRef.current!;
      c.width = Math.round(w * dpr);
      c.height = Math.round(h * dpr);
      c.style.width = `${w}px`;
      c.style.height = `${h}px`;
      if (fitPending.current) fit();
      requestDraw();
    });
    ro.observe(el);
    return () => ro.disconnect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function render() {
    frame.current = undefined;
    if (!dirty.current) return;
    dirty.current = false;
    const c = canvasRef.current;
    const ctx = c?.getContext("2d");
    if (!c || !ctx) return;
    const sel = new Set<number>();
    for (const id of selectedRef.current) {
      const i = indexRef.current.get(id);
      if (i !== undefined) sel.add(i);
    }
    let highlight: Set<number> | null = null;
    if (hover.current !== null) {
      highlight = new Set([hover.current, ...(adjRef.current.get(hover.current) ?? [])]);
    }
    const d = drag.current;
    const toWorld = (x: number, y: number) => ({ x: (x - view.current.x) / view.current.k, y: (y - view.current.y) / view.current.k });
    let connectLine = null;
    if (d?.type === "connect") {
      const a = rnodes.current[d.from];
      if (a) connectLine = { x1: a.x, y1: a.y, x2: d.x, y2: d.y };
    }
    let box = null;
    if (d?.type === "box") {
      const p1 = toWorld(d.x1, d.y1);
      const p2 = toWorld(d.x2, d.y2);
      box = { x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y };
    }
    const edgeIdx = selectedEdgeRef.current ? redges.current.findIndex((e) => e.id === selectedEdgeRef.current) : -1;
    draw(ctx, size.current.w, size.current.h, size.current.dpr, view.current, rnodes.current, redges.current, optsRef.current, {
      selectedNodes: sel,
      selectedEdge: edgeIdx >= 0 ? edgeIdx : null,
      hover: hover.current,
      highlight: highlight && highlight.size > 1 ? highlight : null,
      connectLine,
      box,
    });
  }

  // refs for values used inside render / handlers
  const optsRef = useRef<DrawOptions>({ ...appearance, dark });
  optsRef.current = { routing: appearance.routing, labels: appearance.labels, edgeLabels: appearance.edgeLabels, arrows: appearance.arrows, dark };
  const selectedRef = useRef(selected);
  selectedRef.current = selected;
  const selectedEdgeRef = useRef(selectedEdge);
  selectedEdgeRef.current = selectedEdge;
  const indexRef = useRef(indexOf);
  indexRef.current = indexOf;
  const adjRef = useRef(adjacency);
  adjRef.current = adjacency;

  // read-only handle for automated tests / debugging in the browser console
  (window as any).__bsddGraph = { nodes: () => rnodes.current, edges: () => redges.current, view: () => view.current, running: () => running };

  const fit = () => {
    const nodes = rnodes.current;
    const { w, h } = size.current;
    if (!w || !h) return;
    if (!nodes.length) {
      view.current = { x: w / 2, y: h / 2, k: 1 };
      requestDraw();
      return;
    }
    fitPending.current = false;
    const b = bounds(nodes);
    const k = Math.min(2, Math.max(0.05, Math.min((w - 60) / (b.x1 - b.x0 || 1), (h - 60) / (b.y1 - b.y0 || 1))));
    view.current = { k, x: w / 2 - ((b.x0 + b.x1) / 2) * k, y: h / 2 - ((b.y0 + b.y1) / 2) * k };
    requestDraw();
  };

  const zoom = (factor: number, cx?: number, cy?: number) => {
    const v = view.current;
    const px = cx ?? size.current.w / 2;
    const py = cy ?? size.current.h / 2;
    const k = Math.min(4, Math.max(0.03, v.k * factor));
    view.current = { k, x: px - ((px - v.x) / v.k) * k, y: py - ((py - v.y) / v.k) * k };
    requestDraw();
  };

  // ------------------------------------------------------------------ scene operations

  const addIds = (ids: string[], focus = false) => {
    setScene((s) => {
      const set = new Set(s);
      const next = [...s];
      for (const id of ids) if (!set.has(id)) next.push(id), set.add(id);
      return next;
    });
    if (focus) fitPending.current = true;
  };
  const removeIds = (ids: string[]) => {
    const rm = new Set(ids);
    setScene((s) => s.filter((x) => !rm.has(x)));
    setSelected(new Set());
  };
  const expandIds = (id: string, which?: keyof ReturnType<typeof neighbours>) => {
    if (!doc) return [];
    const n = neighbours(doc, idx, id);
    if (which) return n[which];
    return [...n.parent, ...n.children, ...n.relations, ...n.properties, ...n.classes, ...n.ifc];
  };
  const expand = (id: string, which?: keyof ReturnType<typeof neighbours>) => {
    const ids = expandIds(id, which);
    // place them on a ring around the expanded node
    const center = pos.current.get(id);
    if (center) {
      const fresh = ids.filter((x) => !pos.current.has(x));
      fresh.forEach((x, i) => {
        const a = (i / Math.max(1, fresh.length)) * Math.PI * 2;
        const r = 110 + fresh.length * 4;
        pos.current.set(x, { x: center.x + Math.cos(a) * r, y: center.y + Math.sin(a) * r, fixed: false });
      });
    }
    addIds(ids);
  };

  // drag & drop from the class tree, property tables or the library panel
  const onDragOver = (e: React.DragEvent) => {
    if (!hasGraphDrag(e)) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = "copy";
    if (!dropActive) setDropActive(true);
  };
  const onDrop = (e: React.DragEvent) => {
    setDropActive(false);
    if (!hasGraphDrag(e) || !doc) return;
    e.preventDefault();
    const ids = readGraphDrag(e).filter((id) => describeNode(doc, idx, id, labels));
    if (!ids.length) return;
    const p = toWorld(e);
    const present = new Set(scene);
    const fresh = ids.filter((id) => !present.has(id));
    // drop point = centre of a small grid of the new nodes
    const cols = Math.max(1, Math.ceil(Math.sqrt(fresh.length)));
    const rows = Math.ceil(fresh.length / cols);
    fresh.forEach((id, i) => {
      pendingNew.current.add(id);
      const gx = (i % cols) - (cols - 1) / 2;
      const gy = Math.floor(i / cols) - (rows - 1) / 2;
      pos.current.set(id, { x: p.x + gx * 140, y: p.y + gy * 60, fixed: appearance.pinOnDrag });
    });
    fitPending.current = false; // keep the nodes where they were dropped
    if (fresh.length) {
      pendingAlpha.current = Math.max(pendingAlpha.current ?? 0, 0.3);
      addIds(fresh);
    }
    setSelected(new Set(ids));
    wrapRef.current?.focus();
  };
  const sceneSet = useMemo(() => new Set(scene), [scene]);

  const addFromInput = () => {
    if (!doc) return;
    const id = resolveInput(doc, idx, input);
    if (!id) {
      notifyError(t("Nothing found for '{{text}}'", { text: input }));
      return;
    }
    addIds([id]);
    setSelected(new Set([id]));
    setInput("");
  };

  const addOptions = useMemo(() => {
    if (!doc) return [];
    const classes = (doc.dictionary.Classes ?? []).map((c) => ({ value: classId(c.Code), label: `${c.Name} (${c.Code})` }));
    const props = (doc.dictionary.Properties ?? []).map((p) => ({ value: propId(p.Code), label: `${p.Name} (${p.Code})` }));
    return [
      { group: t("Classes"), items: classes },
      { group: t("Properties"), items: props },
    ];
  }, [doc, t]);

  const setPinned = (ids: string[], value: boolean) => {
    const indices: number[] = [];
    for (const id of ids) {
      const p = pos.current.get(id);
      if (p) p.fixed = value;
      const i = indexOf.get(id);
      if (i !== undefined) {
        rnodes.current[i].fixed = value;
        indices.push(i);
      }
    }
    worker.current?.postMessage({ type: "fixed", indices, value });
    requestDraw();
  };

  // the last tree layout is applied again when the tree order changes
  const lastTree = useRef<"tree-tb" | "tree-lr" | null>(null);
  const applyLayout = (kind: "tree-tb" | "tree-lr" | "circle" | "grid") => {
    lastTree.current = kind === "tree-tb" || kind === "tree-lr" ? kind : null;
    const nodes = rnodes.current;
    const lnodes = nodes.map((n) => ({ id: n.id, w: n.w, h: n.h }));
    const result = kind === "tree-tb" ? treeLayout(lnodes, graph.edges, "TB", treeOrder) : kind === "tree-lr" ? treeLayout(lnodes, graph.edges, "LR", treeOrder) : kind === "circle" ? circleLayout(lnodes) : gridLayout(lnodes);
    const positions = new Float32Array(nodes.length * 2);
    nodes.forEach((n, i) => {
      const p = result.get(n.id) ?? { x: n.x, y: n.y };
      n.x = p.x;
      n.y = p.y;
      positions[2 * i] = p.x;
      positions[2 * i + 1] = p.y;
      const stored = pos.current.get(n.id);
      if (stored) {
        stored.x = p.x;
        stored.y = p.y;
      }
    });
    worker.current?.postMessage({ type: "positions", positions }, [positions.buffer]);
    fit();
  };

  // ------------------------------------------------------------------ dictionary edits

  const deleteEdge = async (edgeId: string) => {
    const e = graph.edges.find((x) => x.id === edgeId);
    if (!e || !doc) return;
    const ok = await askConfirm(t("Delete relation"), t("Delete the relation '{{label}}' from the dictionary?", { label: e.label || e.kind }), t("Delete"), true);
    if (!ok) return;
    const r = e.ref;
    if (r.type === "parent") await attempt(() => op("class.update", { code: r.child, data: { ParentClassCode: null } }));
    else if (r.type === "classRelation") await attempt(() => op("relation.remove", { kind: "class", code: r.owner, index: r.index }));
    else if (r.type === "propertyRelation") await attempt(() => op("relation.remove", { kind: "property", code: r.owner, index: r.index }));
    else if (r.type === "classProperty") await attempt(() => op("cp.delete", { class_code: r.owner, codes: [r.cpCode] }));
    else if (r.type === "ifc") {
      const c = idx.classes.get(r.owner);
      await attempt(() => op("class.update", { code: r.owner, data: { RelatedIfcEntityNamesList: (c?.RelatedIfcEntityNamesList ?? []).filter((x) => x !== r.name) } }));
    }
    setSelectedEdge(null);
  };

  const editNode = (id: string) => {
    if (id.startsWith("c:")) openUi({ classEditor: { code: id.slice(2) } });
    else if (id.startsWith("p:")) openUi({ propertyEditor: { code: id.slice(2) } });
    else if (id.startsWith("xc:") || id.startsWith("xp:")) window.open(id.slice(3), "_blank");
  };

  // ------------------------------------------------------------------ pointer handling

  const toWorld = (e: { clientX: number; clientY: number }) => {
    const rect = canvasRef.current!.getBoundingClientRect();
    const sx = e.clientX - rect.left;
    const sy = e.clientY - rect.top;
    return { sx, sy, x: (sx - view.current.x) / view.current.k, y: (sy - view.current.y) / view.current.k };
  };

  const onPointerDown = (e: React.PointerEvent) => {
    if (e.button === 2) return;
    wrapRef.current?.focus();
    canvasRef.current!.setPointerCapture(e.pointerId);
    const p = toWorld(e);
    const hit = hitNode(rnodes.current, p.x, p.y);
    if (hit !== null && e.button === 0) {
      const id = rnodes.current[hit].id;
      if (e.altKey || connectMode) {
        drag.current = { type: "connect", from: hit, x: p.x, y: p.y };
        return;
      }
      let sel = selected;
      if (e.ctrlKey || e.metaKey || e.shiftKey) {
        sel = new Set(selected);
        if (sel.has(id) && !e.shiftKey) sel.delete(id);
        else sel.add(id);
      } else if (!selected.has(id)) sel = new Set([id]);
      setSelected(sel);
      setSelectedEdge(null);
      const items = [...sel].map((sid) => indexOf.get(sid)).filter((i): i is number => i !== undefined).map((i) => ({ i, dx: rnodes.current[i].x - p.x, dy: rnodes.current[i].y - p.y }));
      drag.current = { type: "nodes", items, moved: false };
      if (id.startsWith("c:")) useProject.getState().setActiveClass(id.slice(2));
      return;
    }
    if (e.button === 0 && !e.shiftKey) {
      const edge = hitEdge(rnodes.current, redges.current, appearance.routing, p.x, p.y, 6 / view.current.k);
      if (edge !== null) {
        setSelectedEdge(redges.current[edge].id);
        setSelected(new Set());
        drag.current = null;
        return;
      }
    }
    if (e.shiftKey && e.button === 0) {
      drag.current = { type: "box", x1: p.sx, y1: p.sy, x2: p.sx, y2: p.sy, add: e.ctrlKey || e.metaKey };
      return;
    }
    if (!(e.ctrlKey || e.metaKey)) {
      setSelected(new Set());
      setSelectedEdge(null);
    }
    drag.current = { type: "pan", sx: e.clientX, sy: e.clientY, vx: view.current.x, vy: view.current.y };
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const p = toWorld(e);
    const d = drag.current;
    if (!d) {
      const h = hitNode(rnodes.current, p.x, p.y);
      if (h !== hover.current) {
        hover.current = h;
        canvasRef.current!.style.cursor = h !== null ? (connectMode ? "crosshair" : "grab") : "default";
        requestDraw();
      }
      return;
    }
    if (d.type === "pan") {
      view.current = { ...view.current, x: d.vx + e.clientX - d.sx, y: d.vy + e.clientY - d.sy };
    } else if (d.type === "nodes") {
      d.moved = true;
      const items: [number, number, number][] = [];
      for (const it of d.items) {
        const n = rnodes.current[it.i];
        n.x = p.x + it.dx;
        n.y = p.y + it.dy;
        n.fixed = true;
        const stored = pos.current.get(n.id);
        if (stored) {
          stored.x = n.x;
          stored.y = n.y;
          stored.fixed = true;
        }
        items.push([it.i, n.x, n.y]);
      }
      worker.current?.postMessage({ type: "drag", items, simulate: appearance.physicsOnDrag });
    } else if (d.type === "box") {
      d.x2 = p.sx;
      d.y2 = p.sy;
    } else if (d.type === "connect") {
      d.x = p.x;
      d.y = p.y;
      hover.current = hitNode(rnodes.current, p.x, p.y);
    }
    requestDraw();
  };

  const onPointerUp = (e: React.PointerEvent) => {
    const d = drag.current;
    drag.current = null;
    if (!d) return;
    if (d.type === "nodes" && d.moved) {
      worker.current?.postMessage({ type: "dragEnd" });
      if (!appearance.pinOnDrag) setPinned(d.items.map((it) => rnodes.current[it.i].id), false);
    } else if (d.type === "box") {
      const a = { x: (Math.min(d.x1, d.x2) - view.current.x) / view.current.k, y: (Math.min(d.y1, d.y2) - view.current.y) / view.current.k };
      const b = { x: (Math.max(d.x1, d.x2) - view.current.x) / view.current.k, y: (Math.max(d.y1, d.y2) - view.current.y) / view.current.k };
      const ids = rnodes.current.filter((n) => n.x >= a.x && n.x <= b.x && n.y >= a.y && n.y <= b.y).map((n) => n.id);
      setSelected(new Set(d.add ? [...selected, ...ids] : ids));
    } else if (d.type === "connect") {
      const p = toWorld(e);
      const target = hitNode(rnodes.current, p.x, p.y);
      if (target !== null && target !== d.from) setConnect({ source: rnodes.current[d.from].id, target: rnodes.current[target].id });
    }
    requestDraw();
  };

  const onWheel = (e: React.WheelEvent) => {
    const p = toWorld(e);
    zoom(Math.exp(-e.deltaY * 0.0015), p.sx, p.sy);
  };

  const onDoubleClick = (e: React.MouseEvent) => {
    const p = toWorld(e);
    const hit = hitNode(rnodes.current, p.x, p.y);
    if (hit !== null) editNode(rnodes.current[hit].id);
    else fit();
  };

  const onContextMenu = (e: React.MouseEvent) => {
    const p = toWorld(e);
    const hit = hitNode(rnodes.current, p.x, p.y);
    if (hit !== null) {
      const node = rnodes.current[hit];
      const id = node.id;
      const ids = selected.has(id) ? [...selected] : [id];
      if (!selected.has(id)) setSelected(new Set([id]));
      const items: MenuItem[] = [
        { label: t("Edit"), onClick: () => editNode(id), disabled: id.startsWith("ifc:") },
        { label: t("Expand all neighbours"), onClick: () => ids.forEach((x) => expand(x)) },
      ];
      if (id.startsWith("c:")) {
        items.push(
          { label: t("Expand parent"), onClick: () => expand(id, "parent") },
          { label: t("Expand children"), onClick: () => expand(id, "children") },
          { label: t("Expand relations"), onClick: () => expand(id, "relations") },
          { label: t("Expand properties"), onClick: () => expand(id, "properties") },
          { label: t("Expand IFC references"), onClick: () => expand(id, "ifc") },
          { label: t("Select in tree"), onClick: () => { useProject.getState().setActiveClass(id.slice(2)); openUi({ revealClass: { code: id.slice(2), at: Date.now() } }); } },
        );
      } else items.push({ label: t("Expand classes"), onClick: () => expand(id, "classes") }, { label: t("Expand relations"), onClick: () => expand(id, "relations") });
      items.push(
        divider,
        { label: t("Start relation from here"), onClick: () => { setConnectMode(true); notifyHint(t("Drag from the node to the target node to create a relation")); } },
        node.fixed ? { label: t("Unpin"), onClick: () => setPinned(ids, false) } : { label: t("Pin"), onClick: () => setPinned(ids, true) },
        divider,
        { label: t("Hide from view"), color: "red", onClick: () => removeIds(ids) },
      );
      openMenu(e, items);
      return;
    }
    const edge = hitEdge(rnodes.current, redges.current, appearance.routing, p.x, p.y, 6 / view.current.k);
    if (edge !== null) {
      const id = redges.current[edge].id;
      setSelectedEdge(id);
      openMenu(e, [{ label: t("Delete relation from dictionary"), color: "red", onClick: () => deleteEdge(id) }]);
      return;
    }
    openMenu(e, [
      { label: t("Fit view"), onClick: fit },
      { label: t("Select all"), onClick: () => setSelected(new Set(graph.nodes.map((n) => n.id))) },
      { label: t("Unpin all"), onClick: () => setPinned(graph.nodes.map((n) => n.id), false) },
    ]);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    const target = e.target as HTMLElement;
    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;
    const k = e.key.toLowerCase();
    if (k === "delete" || k === "backspace") {
      e.preventDefault();
      if (selectedEdge) void deleteEdge(selectedEdge);
      else if (selected.size) removeIds([...selected]);
    } else if ((e.ctrlKey || e.metaKey) && k === "a") {
      e.preventDefault();
      setSelected(new Set(graph.nodes.map((n) => n.id)));
    } else if (k === "f") fit();
    else if (k === " ") {
      e.preventDefault();
      togglePhysics();
    } else if (k === "escape") {
      setConnectMode(false);
      setSelected(new Set());
      setSelectedEdge(null);
    } else if (k === "+" || k === "=") zoom(1.2);
    else if (k === "-") zoom(1 / 1.2);
  };

  const togglePhysics = () => worker.current?.postMessage({ type: running ? "stop" : "start", alpha: 0.6, continuous: true });

  // ------------------------------------------------------------------ export

  const exportName = (ext: string) => `${doc?.dictionary.DictionaryCode ?? "graph"}_graph.${ext}`;
  const exportPng = () => {
    const nodes = rnodes.current;
    const b = bounds(nodes);
    const scale = 2;
    const pad = 40;
    const w = Math.min(16000, (b.x1 - b.x0 + 2 * pad) * scale);
    const h = Math.min(16000, (b.y1 - b.y0 + 2 * pad) * scale);
    const k = Math.min(scale, w / (b.x1 - b.x0 + 2 * pad), h / (b.y1 - b.y0 + 2 * pad));
    const c = document.createElement("canvas");
    c.width = w;
    c.height = h;
    const ctx = c.getContext("2d")!;
    draw(ctx, w, h, 1, { k, x: (-b.x0 + pad) * k, y: (-b.y0 + pad) * k }, nodes, redges.current, { ...optsRef.current, dark: false }, {
      selectedNodes: new Set(),
      selectedEdge: null,
      hover: null,
      highlight: null,
      connectLine: null,
      box: null,
    });
    c.toBlob((blob) => blob && saveBlob(blob, exportName("png")));
  };
  const exportSvg = () => {
    const { svg } = toSvg(rnodes.current, redges.current, { ...optsRef.current, dark: false });
    saveBlob(new Blob([svg], { type: "image/svg+xml" }), exportName("svg"));
  };
  const exportHtml = () => {
    if (!doc) return;
    const tab = buildTab(doc, idx, "", graph.nodes, rnodes.current, graph.edges, optsRef.current);
    saveBlob(new Blob([htmlPage(doc, [tab], optsRef.current.dark)], { type: "text/html" }), exportName("html"));
  };
  // desktop "Export Full HTML (Tabs)": one tab per root class with its whole subtree as a tree
  const exportFullHtml = () => {
    if (!doc) return;
    const tabs = rootClassTabs(doc, idx, optsRef.current, hiddenEdges);
    if (!tabs.length) return exportHtml();
    saveBlob(new Blob([htmlPage(doc, tabs, optsRef.current.dark)], { type: "text/html" }), exportName("full.html"));
    notifyHint(t("{{n}} root classes exported as tabs", { n: tabs.length }));
  };
  const exportScene = () => {
    save();
    saveBlob(new Blob([JSON.stringify(storageGet(storeKey, {}), null, 1)], { type: "application/json" }), exportName("scene.json"));
  };
  const importScene = async (file: File | null) => {
    if (!file) return;
    try {
      const data = JSON.parse(await file.text()) as Partial<Saved>;
      if (!Array.isArray(data.scene)) throw new Error(t("Not a graph scene file"));
      for (const [k, v] of Object.entries(data.pos ?? {})) pos.current.set(k, { x: v[0], y: v[1], fixed: !!v[2] });
      setScene(data.scene);
      if (data.hiddenNodes) setHiddenNodes(new Set(data.hiddenNodes));
      if (data.hiddenEdges) setHiddenEdges(new Set(data.hiddenEdges));
      if (data.treeOrder) setTreeOrder(normalizeTreeOrder(data.treeOrder));
      if (data.physics) setPhysics({ ...DEFAULT_PHYSICS, ...data.physics });
      if (data.appearance) setAppearance({ ...DEFAULT_APPEARANCE, ...data.appearance });
      fitPending.current = true;
    } catch (e) {
      notifyError(e);
    }
  };

  const applyRef = useRef(applyLayout);
  applyRef.current = applyLayout;
  const firstOrder = useRef(true);
  useEffect(() => {
    if (firstOrder.current) {
      firstOrder.current = false;
      return;
    }
    if (lastTree.current) applyRef.current(lastTree.current);
  }, [treeOrder]);

  // ------------------------------------------------------------------ UI

  const nodeCounts = new Map<NodeKind, number>();
  for (const n of graph.all) nodeCounts.set(n.kind, (nodeCounts.get(n.kind) ?? 0) + 1);
  const edgeCounts = new Map<EdgeKind, number>();
  for (const e of graph.allEdges) edgeCounts.set(e.kind, (edgeCounts.get(e.kind) ?? 0) + 1);
  const selectedNode = selected.size === 1 ? graph.nodes.find((n) => selected.has(n.id)) : undefined;
  const selEdge = selectedEdge ? graph.edges.find((e) => e.id === selectedEdge) : undefined;
  const physicsSlider = (key: keyof Physics, label: string, min: number, max: number, step: number) => (
    <div>
      <Group justify="space-between"><Text size="xs">{label}</Text><Text size="xs" c="dimmed">{physics[key]}</Text></Group>
      <Slider size="sm" min={min} max={max} step={step} value={physics[key]} onChange={(v) => setPhysics((p) => ({ ...p, [key]: v }))} label={null} />
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      <Group gap={6} p={6} wrap="nowrap" className="graph-toolbar" style={{ borderBottom: "1px solid var(--mantine-color-default-border)" }}>
        <Autocomplete
          placeholder={t("Add node: name, code or URI…")}
          data={addOptions}
          value={input}
          onChange={setInput}
          onOptionSubmit={(v) => { addIds([v]); setSelected(new Set([v])); setTimeout(() => setInput(""), 0); }}
          onKeyDown={(e) => e.key === "Enter" && addFromInput()}
          limit={40}
          w={narrow ? 170 : 300}
          style={{ flex: "none" }}
          comboboxProps={{ zIndex: 1000 }}
        />
        <Tooltip label={t("Add")}><ActionIcon aria-label={t("Add")} variant="light" onClick={addFromInput}><IconPlus size={16} /></ActionIcon></Tooltip>
        <Menu shadow="md" zIndex={1000}>
          <Menu.Target><Button variant="default">{t("Add…")}</Button></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item disabled={!activeClass} onClick={() => activeClass && addIds([classId(activeClass)])}>{t("Active class")}</Menu.Item>
            <Menu.Item disabled={!selectedClasses.length} onClick={() => addIds(selectedClasses.map(classId))}>{t("Classes selected in the tree")}</Menu.Item>
            <Menu.Item onClick={() => addIds((doc?.dictionary.Classes ?? []).filter((c) => c.ClassType !== GOP && c.ClassType !== MATERIAL).map((c) => classId(c.Code)), true)}>{t("All classes")}</Menu.Item>
            <Menu.Item onClick={() => addIds((doc?.dictionary.Classes ?? []).filter((c) => c.ClassType === "GroupOfProperties").map((c) => classId(c.Code)), true)}>{t("All groups of properties")}</Menu.Item>
            <Menu.Item onClick={() => addIds((doc?.dictionary.Classes ?? []).filter((c) => c.ClassType === MATERIAL).map((c) => classId(c.Code)), true)}>{t("All materials")}</Menu.Item>
            <Menu.Item onClick={() => addIds((doc?.dictionary.Properties ?? []).map((p) => propId(p.Code)), true)}>{t("All properties")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item disabled={!selected.size} onClick={() => [...selected].forEach((id) => expand(id))}>{t("Neighbours of the selection")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Tooltip label={t("Hide selected nodes")}><ActionIcon aria-label={t("Hide selected nodes")} variant="default" disabled={!selected.size} onClick={() => removeIds([...selected])}><IconEraser size={16} /></ActionIcon></Tooltip>
        <Tooltip label={t("Clear view")}><ActionIcon aria-label={t("Clear view")} variant="default" onClick={() => { setScene([]); setSelected(new Set()); }}><IconTrash size={16} /></ActionIcon></Tooltip>
        <Divider orientation="vertical" />
        <Tooltip label={running ? t("Pause physics (Space)") : t("Run physics (Space)")}>
          <ActionIcon aria-label={running ? t("Pause physics (Space)") : t("Run physics (Space)")} variant={running ? "filled" : "default"} onClick={togglePhysics}>{running ? <IconPlayerPause size={16} /> : <IconPlayerPlay size={16} />}</ActionIcon>
        </Tooltip>
        <Tooltip label={t("Reheat (shake up the layout)")}><ActionIcon aria-label={t("Reheat (shake up the layout)")} variant="default" onClick={() => worker.current?.postMessage({ type: "start", alpha: 1 })}><IconRefresh size={16} /></ActionIcon></Tooltip>
        <Menu shadow="md" zIndex={1000}>
          <Menu.Target><Button variant="default" leftSection={<IconLayoutGrid size={14} />}>{t("Layout")}</Button></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item onClick={() => worker.current?.postMessage({ type: "start", alpha: 1 })}>{t("Force-directed")}</Menu.Item>
            <Menu.Item onClick={() => applyLayout("tree-tb")}>{t("Tree (top → bottom)")}</Menu.Item>
            <Menu.Item onClick={() => applyLayout("tree-lr")}>{t("Tree (left → right)")}</Menu.Item>
            <Menu.Item onClick={() => applyLayout("circle")}>{t("Circle")}</Menu.Item>
            <Menu.Item onClick={() => applyLayout("grid")}>{t("Grid")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Tooltip label={t("Create relations by dragging from node to node (or hold Alt)")}>
          <Button data-edit variant={connectMode ? "filled" : "default"} color={connectMode ? "yellow" : undefined} onClick={() => setConnectMode((v) => !v)}>{t("Connect")}</Button>
        </Tooltip>
        <div style={{ flex: 1 }} />
        <Badge variant="light">{graph.nodes.length} {t("nodes")} · {graph.edges.length} {t("edges")}</Badge>
        <Tooltip label={t("Zoom in")}><ActionIcon aria-label={t("Zoom in")} variant="default" onClick={() => zoom(1.25)}><IconZoomIn size={16} /></ActionIcon></Tooltip>
        <Tooltip label={t("Zoom out")}><ActionIcon aria-label={t("Zoom out")} variant="default" onClick={() => zoom(0.8)}><IconZoomOut size={16} /></ActionIcon></Tooltip>
        <Tooltip label={t("Fit view (F)")}><ActionIcon aria-label={t("Fit view (F)")} variant="default" onClick={fit}><IconArrowsMaximize size={16} /></ActionIcon></Tooltip>
        <Menu shadow="md" zIndex={1000}>
          <Menu.Target><ActionIcon variant="default" aria-label={t("Export")}><IconDownload size={16} /></ActionIcon></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item onClick={exportPng}>PNG</Menu.Item>
            <Menu.Item onClick={exportSvg}>SVG</Menu.Item>
            <Menu.Item onClick={exportHtml}>{t("Interactive HTML")}</Menu.Item>
            <Menu.Item onClick={exportFullHtml}>{t("Full HTML (one tab per root class)")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item onClick={exportScene}>{t("Save scene (JSON)")}</Menu.Item>
            <FileButton onChange={importScene} accept="application/json,.json">{(props) => <Menu.Item {...props} closeMenuOnClick={false}>{t("Load scene (JSON)")}</Menu.Item>}</FileButton>
          </Menu.Dropdown>
        </Menu>
        {!standalone && (
          <Tooltip label={t("Open in a new window")}><ActionIcon aria-label={t("Open in a new window")} variant="default" component="a" href={`${useProject.getState().base}/${projectId}/window/graph`} target="_blank"><IconExternalLink size={16} /></ActionIcon></Tooltip>
        )}
        <Tooltip
          multiline
          w={320}
          label={t("Drag nodes to move (they get pinned). Drag the background to pan, wheel to zoom, Shift+drag to box-select. Alt+drag (or Connect) from node to node creates a relation. Right-click for more. Del hides nodes / deletes the selected relation, Space toggles physics, F fits the view.")}
        >
          <ActionIcon aria-label={t("Drag nodes to move (they get pinned). Drag the background to pan, wheel to zoom, Shift+drag to box-select. Alt+drag (or Connect) from node to node creates a relation. Right-click for more. Del hides nodes / deletes the selected relation, Space toggles physics, F fits the view.")} variant="subtle"><IconHelp size={16} /></ActionIcon>
        </Tooltip>
        <Tooltip label={t("Dictionary panel (drag classes and properties into the graph)")}>
          <ActionIcon variant={library ? "light" : "subtle"} aria-label={t("Dictionary panel")} onClick={() => { setLibrary((v) => !v); if (narrow) setPanel(false); }}><IconBooks size={16} /></ActionIcon>
        </Tooltip>
        <ActionIcon variant={narrow && panel ? "light" : "subtle"} aria-label={t("Display settings")} onClick={() => { setPanel((v) => !v); if (narrow) setLibrary(false); }}>{panel ? <IconChevronRight size={16} /> : <IconChevronLeft size={16} />}</ActionIcon>
      </Group>

      <div style={{ flex: 1, display: "flex", minHeight: 0, position: "relative" }}>
        {library && doc && (
          <div style={{ width: libraryWidth, flex: "none", borderRight: "1px solid var(--mantine-color-default-border)", minHeight: 0, ...overlay("left") }}>
            <GraphLibrary doc={doc} idx={idx} inScene={sceneSet} onAdd={(ids) => { addIds(ids); setSelected(new Set(ids)); }} />
          </div>
        )}
        {library && doc && !narrow && (
          <div
            className="split-handle"
            role="separator"
            aria-orientation="vertical"
            aria-label={t("Resize dictionary panel")}
            aria-valuenow={libraryWidth}
            aria-valuemin={LIBRARY_MIN}
            aria-valuemax={LIBRARY_MAX}
            tabIndex={0}
            title={t("Drag to resize, double-click to reset")}
            onPointerDown={(e) => {
              libraryDrag.current = { start: e.clientX, initial: libraryWidth };
              document.body.classList.add("resizing");
              e.preventDefault();
            }}
            onDoubleClick={() => resizeLibrary(LIBRARY_DEFAULT)}
            onKeyDown={(e) => {
              if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
                e.preventDefault();
                resizeLibrary(libraryWidth + (e.key === "ArrowRight" ? 20 : -20));
              }
            }}
          />
        )}
        <div
          ref={wrapRef}
          style={{ flex: 1, position: "relative", minWidth: 0, outline: dropActive ? "2px dashed var(--mantine-color-blue-5)" : "none", outlineOffset: -4 }}
          tabIndex={0}
          onKeyDown={onKeyDown}
          onDragOver={onDragOver}
          onDragEnter={onDragOver}
          onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget as Node | null)) setDropActive(false); }}
          onDrop={onDrop}
        >
          <canvas
            ref={canvasRef}
            style={{ position: "absolute", inset: 0, touchAction: "none" }}
            onPointerDown={(e) => {
              if (narrow && (panel || library)) {
                // tapping the graph closes an open overlay panel
                setPanel(false);
                setLibrary(false);
              }
              onPointerDown(e);
            }}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
            onPointerLeave={() => { if (!drag.current && hover.current !== null) { hover.current = null; requestDraw(); } }}
            onWheel={onWheel}
            onDoubleClick={onDoubleClick}
            onContextMenu={onContextMenu}
          />
          {graph.nodes.length === 0 && (
            <Stack align="center" justify="center" style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
              <Text c="dimmed">{t("The view is empty. Drag classes or properties here, or use the search field or the 'Add…' menu.")}</Text>
            </Stack>
          )}
          {!ready && <Text size="xs" c="dimmed" style={{ position: "absolute", left: 8, bottom: 6 }}>{t("Loading physics engine…")}</Text>}
          {connectMode && <Badge color="yellow" style={{ position: "absolute", left: 8, top: 8 }}>{t("Connect mode: drag from a node to another node")}</Badge>}
        </div>

        {panel && (
          <div style={{ width: 290, flex: "none", borderLeft: "1px solid var(--mantine-color-default-border)", overflow: "auto", ...overlay("right") }}>
            {(selectedNode || selEdge) && (
              <Stack gap={4} p="sm" style={{ borderBottom: "1px solid var(--mantine-color-default-border)" }}>
                {selectedNode && (
                  <>
                    <Group gap={6}><span style={{ width: 10, height: 10, borderRadius: 2, background: NODE_STYLE[selectedNode.kind].color }} /><Text fw={600} size="sm">{selectedNode.label}</Text></Group>
                    <Text size="xs" c="dimmed">{t(selectedNode.kind)}</Text>
                    {Object.entries(selectedNode.info ?? {}).filter(([, v]) => v).map(([k, v]) => <Text key={k} size="xs" lineClamp={4}><b>{t(k)}:</b> {v}</Text>)}
                    <Group gap={4} mt={4}>
                      {!selectedNode.id.startsWith("ifc:") && <Button size="compact-xs" variant="light" onClick={() => editNode(selectedNode.id)}>{t("Edit")}</Button>}
                      <Button size="compact-xs" variant="light" onClick={() => expand(selectedNode.id)}>{t("Expand")}</Button>
                    </Group>
                  </>
                )}
                {selEdge && (
                  <>
                    <Text fw={600} size="sm">{selEdge.label || selEdge.kind}</Text>
                    <Text size="xs">{describeNode(doc!, idx, selEdge.source, labels)?.label} → {describeNode(doc!, idx, selEdge.target, labels)?.label}</Text>
                    <Button size="compact-xs" color="red" variant="light" onClick={() => deleteEdge(selEdge.id)}>{t("Delete relation from dictionary")}</Button>
                  </>
                )}
              </Stack>
            )}
            <Accordion multiple defaultValue={["nodes", "edges", "tree", "physics", "appearance"]} variant="contained" radius={0}>
              <Accordion.Item value="nodes">
                <Accordion.Control><Text size="sm" fw={600}>{t("Node types")}</Text></Accordion.Control>
                <Accordion.Panel>
                  <Stack gap={4}>
                    {NODE_KINDS.map((k) => (
                      <Toggle
                        key={k}
                        checked={!hiddenNodes.has(k)}
                        onChange={(e) => setHiddenNodes((s) => { const n = new Set(s); if (e.currentTarget.checked) n.delete(k); else n.add(k); return n; })}
                        label={<Group gap={6} wrap="nowrap"><span style={{ width: 12, height: 10, borderRadius: 2, background: NODE_STYLE[k].color, border: NODE_STYLE[k].dashed ? "1px dashed #000" : undefined }} />{t(k)} <Text span size="xs" c="dimmed">{nodeCounts.get(k) ?? 0}</Text></Group>}
                      />
                    ))}
                  </Stack>
                </Accordion.Panel>
              </Accordion.Item>
              <Accordion.Item value="edges">
                <Accordion.Control><Text size="sm" fw={600}>{t("Edge types")}</Text></Accordion.Control>
                <Accordion.Panel>
                  <Group gap={4} mb={4}>
                    <Button size="compact-xs" variant="subtle" onClick={() => setHiddenEdges(new Set())}>{t("All")}</Button>
                    <Button size="compact-xs" variant="subtle" onClick={() => setHiddenEdges(new Set(EDGE_KINDS))}>{t("None")}</Button>
                  </Group>
                  <Stack gap={4}>
                    {EDGE_KINDS.map((k) => (
                      <Toggle
                        key={k}
                        checked={!hiddenEdges.has(k)}
                        onChange={(e) => setHiddenEdges((s) => { const n = new Set(s); if (e.currentTarget.checked) n.delete(k); else n.add(k); return n; })}
                        label={
                          <Group gap={6} wrap="nowrap">
                            <svg width="26" height="8"><line x1="0" y1="4" x2="26" y2="4" stroke={EDGE_STYLE[k].color} strokeWidth="2" strokeDasharray={EDGE_STYLE[k].dash.join(" ")} /></svg>
                            {t(edgeKindLabel(k))} <Text span size="xs" c="dimmed">{edgeCounts.get(k) ?? 0}</Text>
                          </Group>
                        }
                      />
                    ))}
                  </Stack>
                </Accordion.Panel>
              </Accordion.Item>
              <Accordion.Item value="tree">
                <Accordion.Control><Text size="sm" fw={600}>{t("Tree layout order")}</Text></Accordion.Control>
                <Accordion.Panel>
                  <Text size="xs" c="dimmed" mb={6}>
                    {t("The tree layouts first build a tree from the first edge type. Nodes it does not place under a parent are placed by the second edge type, and so on. Hidden edge types are skipped.")}
                  </Text>
                  <Stack gap={2} aria-label={t("Tree layout order")}>
                    {treeOrder.map((k, i) => {
                      const move = (by: number) =>
                        setTreeOrder((o) => {
                          const n = [...o];
                          [n[i], n[i + by]] = [n[i + by], n[i]];
                          return n;
                        });
                      const hidden = hiddenEdges.has(k);
                      return (
                        <Group key={k} gap={4} wrap="nowrap" data-tree-kind={k} style={{ opacity: hidden ? 0.45 : 1 }}>
                          <Text size="xs" c="dimmed" w={16} ta="right">{i + 1}.</Text>
                          <svg width="20" height="8" style={{ flex: "none" }}><line x1="0" y1="4" x2="20" y2="4" stroke={EDGE_STYLE[k].color} strokeWidth="2" strokeDasharray={EDGE_STYLE[k].dash.join(" ")} /></svg>
                          <Text size="xs" style={{ flex: 1, minWidth: 0 }} truncate title={t(edgeKindLabel(k))}>{t(edgeKindLabel(k))}{hidden ? ` (${t("hidden")})` : ""}</Text>
                          <ActionIcon size="xs" variant="subtle" disabled={i === 0} aria-label={t("Move {{name}} up", { name: t(edgeKindLabel(k)) })} onClick={() => move(-1)}><IconChevronUp size={12} /></ActionIcon>
                          <ActionIcon size="xs" variant="subtle" disabled={i === treeOrder.length - 1} aria-label={t("Move {{name}} down", { name: t(edgeKindLabel(k)) })} onClick={() => move(1)}><IconChevronDown size={12} /></ActionIcon>
                        </Group>
                      );
                    })}
                  </Stack>
                  <Group gap={4} mt={6}>
                    <Button size="compact-xs" variant="light" onClick={() => applyLayout("tree-tb")}>{t("Tree (top → bottom)")}</Button>
                    <Button size="compact-xs" variant="light" onClick={() => applyLayout("tree-lr")}>{t("Tree (left → right)")}</Button>
                    <Button size="compact-xs" variant="subtle" onClick={() => setTreeOrder([...TREE_EDGE_KINDS])}>{t("Default order")}</Button>
                  </Group>
                </Accordion.Panel>
              </Accordion.Item>
              <Accordion.Item value="physics">
                <Accordion.Control><Text size="sm" fw={600}>{t("Physics")}</Text></Accordion.Control>
                <Accordion.Panel>
                  <Stack gap={6}>
                    {physicsSlider("repulsion", t("Repulsion"), 0, 6000, 50)}
                    {physicsSlider("springLength", t("Edge length"), 10, 400, 5)}
                    {physicsSlider("springK", t("Edge stiffness"), 0, 0.3, 0.005)}
                    {physicsSlider("gravity", t("Gravity"), 0, 0.2, 0.005)}
                    {physicsSlider("damping", t("Friction"), 0, 0.95, 0.05)}
                    {physicsSlider("collision", t("Overlap avoidance"), 0, 1, 0.1)}
                    {physicsSlider("theta", t("Approximation (Barnes-Hut θ)"), 0.3, 1.5, 0.05)}
                    {physicsSlider("maxSpeed", t("Max. speed"), 5, 200, 5)}
                    <Switch label={t("Simulate while dragging")} checked={appearance.physicsOnDrag} onChange={(e) => setAppearance((a) => ({ ...a, physicsOnDrag: e.currentTarget.checked }))} />
                    <Switch label={t("Pin nodes after dragging")} checked={appearance.pinOnDrag} onChange={(e) => setAppearance((a) => ({ ...a, pinOnDrag: e.currentTarget.checked }))} />
                    <Group gap={4}>
                      <Button size="compact-xs" variant="light" onClick={() => setPinned(graph.nodes.map((n) => n.id), false)}>{t("Unpin all")}</Button>
                      <Button size="compact-xs" variant="subtle" onClick={() => setPhysics(DEFAULT_PHYSICS)}>{t("Defaults")}</Button>
                    </Group>
                  </Stack>
                </Accordion.Panel>
              </Accordion.Item>
              <Accordion.Item value="appearance">
                <Accordion.Control><Text size="sm" fw={600}>{t("Appearance")}</Text></Accordion.Control>
                <Accordion.Panel>
                  <Stack gap={6}>
                    <Text size="xs">{t("Edge routing")}</Text>
                    <SegmentedControl
                      size="xs"
                      fullWidth
                      value={appearance.routing}
                      onChange={(v) => setAppearance((a) => ({ ...a, routing: v as Routing }))}
                      data={[{ value: "straight", label: t("Straight") }, { value: "orthogonal", label: t("Right-angle") }, { value: "curved", label: t("Curved") }]}
                    />
                    <Switch label={t("Node labels")} checked={appearance.labels} onChange={(e) => setAppearance((a) => ({ ...a, labels: e.currentTarget.checked }))} />
                    <Switch label={t("Edge labels")} checked={appearance.edgeLabels} onChange={(e) => setAppearance((a) => ({ ...a, edgeLabels: e.currentTarget.checked }))} />
                    <Switch label={t("Arrows")} checked={appearance.arrows} onChange={(e) => setAppearance((a) => ({ ...a, arrows: e.currentTarget.checked }))} />
                  </Stack>
                </Accordion.Panel>
              </Accordion.Item>
            </Accordion>
          </div>
        )}
      </div>
      <ConnectDialog value={connect} onClose={() => { setConnect(null); setConnectMode(false); }} />
    </div>
  );
}

function notifyHint(message: string) {
  import("@mantine/notifications").then(({ notifications }) => notifications.show({ message, autoClose: 4000 }));
}


// ------------------------------------------------------------------ create relations by connecting nodes

function ConnectDialog({ value, onClose }: { value: { source: string; target: string } | null; onClose: () => void }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const [type, setType] = useState<string | null>(null);
  const options = useMemo(() => {
    if (!value) return [];
    const s = value.source;
    const tg = value.target;
    const isClass = (id: string) => id.startsWith("c:");
    const isProp = (id: string) => id.startsWith("p:") || id.startsWith("xp:");
    if (isClass(s) && (isClass(tg) || tg.startsWith("xc:"))) {
      const list = CLASS_RELATION_TYPES.map((r) => ({ value: r, label: r }));
      if (isClass(tg)) list.unshift({ value: "__parent", label: t("Parent class (ParentClassCode)") });
      return list;
    }
    if ((isClass(s) && isProp(tg)) || (isProp(s) && isClass(tg))) return [{ value: "__cp", label: t("Add as class property") }];
    if (s.startsWith("p:") && isProp(tg)) return PROPERTY_RELATION_TYPES.map((r) => ({ value: r, label: r }));
    if ((isClass(s) && tg.startsWith("ifc:")) || (s.startsWith("ifc:") && isClass(tg))) return [{ value: "__ifc", label: t("Related IFC entity") }];
    return [];
  }, [value, t]);

  useEffect(() => setType(options[0]?.value ?? null), [options]);
  if (!value || !doc) return null;
  const name = (id: string) => describeNode(doc, idx, id)?.label ?? id;

  const create = async () => {
    if (!type) return;
    const s = value.source;
    const tg = value.target;
    const uriOrCode = (id: string) => (id.startsWith("c:") || id.startsWith("p:") ? id.slice(2) : id.slice(3));
    let ok: unknown;
    if (type === "__parent") ok = await attempt(() => op("class.update", { code: s.slice(2), data: { ParentClassCode: tg.slice(2) } }));
    else if (type === "__cp") {
      const [cls, prop] = s.startsWith("c:") ? [s, tg] : [tg, s];
      ok = prop.startsWith("p:")
        ? await attempt(() => op("cp.add_properties", { class_code: cls.slice(2), property_codes: [prop.slice(2)] }))
        : await attempt(() => op("cp.create", { class_code: cls.slice(2), data: { PropertyUri: prop.slice(3), PropertySet: "ExternalPset" } }));
    } else if (type === "__ifc") {
      const [cls, ifc] = s.startsWith("c:") ? [s, tg] : [tg, s];
      const c = idx.classes.get(cls.slice(2));
      ok = await attempt(() => op("class.update", { code: cls.slice(2), data: { RelatedIfcEntityNamesList: [...new Set([...(c?.RelatedIfcEntityNamesList ?? []), ifc.slice(4)])] } }));
    } else if (s.startsWith("c:")) ok = await attempt(() => op("relation.add", { kind: "class", code: s.slice(2), relation: { RelationType: type, RelatedClassUri: uriOrCode(tg) } }));
    else ok = await attempt(() => op("relation.add", { kind: "property", code: s.slice(2), relation: { RelationType: type, RelatedPropertyUri: uriOrCode(tg) } }));
    if (ok !== undefined) onClose();
  };

  return (
    <Modal opened onClose={onClose} title={t("Create relation")} zIndex={1000}>
      <Stack>
        <Text size="sm"><b>{name(value.source)}</b> → <b>{name(value.target)}</b></Text>
        {options.length ? (
          <Select label={t("Relation type")} data={options} value={type} onChange={setType} allowDeselect={false} comboboxProps={{ zIndex: 1100 }} />
        ) : (
          <Text size="sm" c="red">{t("These two node types cannot be connected.")}</Text>
        )}
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>{t("Cancel")}</Button>
          <Button onClick={create} disabled={!type}>{t("Create")}</Button>
        </Group>
      </Stack>
    </Modal>
  );
}
