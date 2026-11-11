/** Static layouts: tidy tree (top-down / left-right), circle and grid. */
import type { EdgeKind, GEdge } from "./model";

export interface LayoutNode {
  id: string;
  w: number;
  h: number;
}

type Pos = Map<string, { x: number; y: number }>;

/** Edge kinds that define a hierarchy, as [kind, sourceIsChild]. */
const HIERARCHY: Partial<Record<EdgeKind, boolean>> = {
  ParentClassCode: true, // child -> parent
  IsChildOf: true,
  IsPartOf: true,
  IsParentOf: false, // parent -> child
  HasPart: false,
  ClassProperty: false,
  GopProperty: false,
  IfcReference: false,
  HasMaterial: false,
  HasReference: false,
};

/** Edge kinds that can build the tree, in the default order (stronger hierarchy first). */
export const TREE_EDGE_KINDS: EdgeKind[] = [
  "ParentClassCode",
  "IsChildOf",
  "IsParentOf",
  "IsPartOf",
  "HasPart",
  "ClassProperty",
  "GopProperty",
  "HasMaterial",
  "IfcReference",
  "HasReference",
];

/** A saved order completed with kinds it does not know yet (e.g. after an update). */
export function normalizeTreeOrder(order: readonly string[] | undefined): EdgeKind[] {
  const known = (order ?? []).filter((k): k is EdgeKind => (TREE_EDGE_KINDS as string[]).includes(k));
  const out = [...new Set(known)];
  for (const k of TREE_EDGE_KINDS) if (!out.includes(k)) out.push(k);
  return out;
}

/**
 * Tidy tree. The trees are built from the edges of ``order[0]`` first; nodes that are not part of
 * those trees (neither as parent nor as child) are placed by ``order[1]``, and so on. A node keeps
 * the place it got from an earlier edge type, and gets at most one parent.
 */
export function treeLayout(nodes: LayoutNode[], edges: GEdge[], direction: "TB" | "LR", order: readonly EdgeKind[] = TREE_EDGE_KINDS): Pos {
  const ids = new Set(nodes.map((n) => n.id));
  const size = new Map(nodes.map((n) => [n.id, n]));
  const parent = new Map<string, string>();
  // nodes that are part of the tree of an earlier edge type (as parent or child) stay where they are
  const placed = new Set<string>();
  for (const kind of order) {
    if (!(kind in HIERARCHY)) continue;
    const childIsSource = HIERARCHY[kind];
    const placedNow: string[] = [];
    for (const e of edges) {
      if (e.kind !== kind || !ids.has(e.source) || !ids.has(e.target)) continue;
      const [child, par] = childIsSource ? [e.source, e.target] : [e.target, e.source];
      if (parent.has(child) || placed.has(child) || child === par) continue;
      // avoid cycles
      let cur: string | undefined = par;
      let cycle = false;
      while (cur) {
        if (cur === child) {
          cycle = true;
          break;
        }
        cur = parent.get(cur);
      }
      if (!cycle) {
        parent.set(child, par);
        placedNow.push(child, par);
      }
    }
    for (const id of placedNow) placed.add(id);
  }
  const children = new Map<string, string[]>();
  for (const n of nodes) {
    const p = parent.get(n.id);
    if (p) {
      if (!children.has(p)) children.set(p, []);
      children.get(p)!.push(n.id);
    }
  }
  const roots = nodes.filter((n) => !parent.has(n.id)).map((n) => n.id);
  // roots with children first, singletons at the end
  roots.sort((a, b) => (children.get(b)?.length ?? 0) - (children.get(a)?.length ?? 0));

  const GAP_SIBLING = 24;
  const GAP_LEVEL = 70;
  const breadth = (id: string) => (direction === "TB" ? size.get(id)!.w : size.get(id)!.h);
  const depthSize = (id: string) => (direction === "TB" ? size.get(id)!.h : size.get(id)!.w);

  // level offsets (max node depth-size per level)
  const levelSize: number[] = [];
  const depthOf = new Map<string, number>();
  const visit = (id: string, depth: number) => {
    depthOf.set(id, depth);
    levelSize[depth] = Math.max(levelSize[depth] ?? 0, depthSize(id));
    for (const c of children.get(id) ?? []) visit(c, depth + 1);
  };
  roots.forEach((r) => visit(r, 0));
  const levelPos: number[] = [];
  let acc = 0;
  for (let i = 0; i < levelSize.length; i++) {
    levelPos[i] = acc + levelSize[i] / 2;
    acc += levelSize[i] + GAP_LEVEL;
  }

  // subtree packing: returns span used
  const pos: Pos = new Map();
  let cursor = 0;
  const place = (id: string): number => {
    const kids = children.get(id) ?? [];
    let center: number;
    if (!kids.length) {
      const b = breadth(id);
      center = cursor + b / 2;
      cursor += b + GAP_SIBLING;
    } else {
      const centers = kids.map(place);
      center = (centers[0] + centers[centers.length - 1]) / 2;
      // make sure the parent itself fits
      const b = breadth(id);
      if (cursor < center + b / 2 + GAP_SIBLING) cursor = Math.max(cursor, center + b / 2 + GAP_SIBLING);
    }
    const level = levelPos[depthOf.get(id) ?? 0];
    pos.set(id, direction === "TB" ? { x: center, y: level } : { x: level, y: center });
    return center;
  };
  for (const r of roots) {
    place(r);
    cursor += GAP_SIBLING * 2;
  }
  return center(pos);
}

export function circleLayout(nodes: LayoutNode[]): Pos {
  const pos: Pos = new Map();
  const total = nodes.reduce((s, n) => s + Math.max(n.w, n.h) + 20, 0);
  const r = Math.max(100, total / (2 * Math.PI));
  let acc = 0;
  for (const n of nodes) {
    const step = Math.max(n.w, n.h) + 20;
    const a = ((acc + step / 2) / total) * 2 * Math.PI;
    pos.set(n.id, { x: Math.cos(a) * r, y: Math.sin(a) * r });
    acc += step;
  }
  return pos;
}

export function gridLayout(nodes: LayoutNode[]): Pos {
  const pos: Pos = new Map();
  const cols = Math.max(1, Math.ceil(Math.sqrt(nodes.length)));
  const cw = Math.max(80, ...nodes.map((n) => n.w)) + 30;
  const ch = Math.max(30, ...nodes.map((n) => n.h)) + 40;
  nodes.forEach((n, i) => pos.set(n.id, { x: (i % cols) * cw, y: Math.floor(i / cols) * ch }));
  return center(pos);
}

function center(pos: Pos): Pos {
  let x0 = Infinity,
    y0 = Infinity,
    x1 = -Infinity,
    y1 = -Infinity;
  for (const p of pos.values()) {
    x0 = Math.min(x0, p.x);
    y0 = Math.min(y0, p.y);
    x1 = Math.max(x1, p.x);
    y1 = Math.max(y1, p.y);
  }
  const cx = (x0 + x1) / 2;
  const cy = (y0 + y1) / 2;
  for (const p of pos.values()) {
    p.x -= cx;
    p.y -= cy;
  }
  return pos;
}

/**
 * Arrange the connected parts of a layout (e.g. the trees of a forest) in rows so the whole
 * picture roughly matches the aspect ratio of the view instead of one long strip.
 */
export function packComponents(pos: Pos, nodes: LayoutNode[], edges: GEdge[], aspect: number): Pos {
  const ids = new Set(nodes.map((n) => n.id));
  const up = new Map<string, string>();
  const find = (x: string): string => {
    let r = x;
    while (up.has(r)) r = up.get(r)!;
    if (r !== x) up.set(x, r);
    return r;
  };
  for (const e of edges) {
    if (!ids.has(e.source) || !ids.has(e.target)) continue;
    const a = find(e.source);
    const b = find(e.target);
    if (a !== b) up.set(a, b);
  }
  const boxes = new Map<string, { ids: string[]; x0: number; y0: number; x1: number; y1: number }>();
  for (const n of nodes) {
    const p = pos.get(n.id);
    if (!p) continue;
    const r = find(n.id);
    const b = boxes.get(r) ?? { ids: [], x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
    b.ids.push(n.id);
    b.x0 = Math.min(b.x0, p.x - n.w / 2);
    b.x1 = Math.max(b.x1, p.x + n.w / 2);
    b.y0 = Math.min(b.y0, p.y - n.h / 2);
    b.y1 = Math.max(b.y1, p.y + n.h / 2);
    boxes.set(r, b);
  }
  const list = [...boxes.values()];
  if (list.length < 2) return pos;
  const GAP = 60;
  const area = list.reduce((s, b) => s + (b.x1 - b.x0 + GAP) * (b.y1 - b.y0 + GAP), 0);
  const rowWidth = Math.max(...list.map((b) => b.x1 - b.x0), Math.sqrt(area * Math.max(0.3, aspect)));
  const out: Pos = new Map();
  let x = 0;
  let y = 0;
  let rowHeight = 0;
  for (const b of list) {
    const w = b.x1 - b.x0;
    const h = b.y1 - b.y0;
    if (x > 0 && x + w > rowWidth) {
      x = 0;
      y += rowHeight + GAP;
      rowHeight = 0;
    }
    for (const id of b.ids) {
      const p = pos.get(id)!;
      out.set(id, { x: p.x - b.x0 + x, y: p.y - b.y0 + y });
    }
    x += w + GAP;
    rowHeight = Math.max(rowHeight, h);
  }
  return center(out);
}
