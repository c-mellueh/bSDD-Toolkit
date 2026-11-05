/** Canvas renderer for the graph viewer: batched drawing, level of detail, hit testing, SVG export. */
import { EDGE_STYLE, NODE_STYLE, type EdgeKind, type GEdge, type NodeKind } from "./model";

export type Routing = "straight" | "orthogonal" | "curved";

export interface RNode {
  id: string;
  kind: NodeKind;
  label: string; // display label (already truncated)
  x: number;
  y: number;
  w: number;
  h: number;
  fixed: boolean;
}

export interface REdge {
  id: string;
  s: number;
  t: number;
  kind: EdgeKind;
  label: string;
  lane: number; // index among parallel edges of the same node pair
  lanes: number;
}

export interface DrawOptions {
  routing: Routing;
  labels: boolean;
  edgeLabels: boolean;
  arrows: boolean;
  dark: boolean;
}

export interface Overlay {
  selectedNodes: Set<number>;
  selectedEdge: number | null;
  hover: number | null;
  highlight: Set<number> | null; // nodes to emphasise (hover neighbourhood)
  connectLine: { x1: number; y1: number; x2: number; y2: number } | null;
  box: { x1: number; y1: number; x2: number; y2: number } | null;
}

export interface View {
  x: number;
  y: number;
  k: number;
}

interface Geometry {
  type: "poly" | "quad";
  pts: number[]; // poly: x0,y0,x1,y1,...  quad: x0,y0,cx,cy,x1,y1
}

const FONT = "12px Inter, system-ui, sans-serif";

let measureCtx: CanvasRenderingContext2D | null = null;
export function measure(text: string): number {
  if (!measureCtx) {
    measureCtx = document.createElement("canvas").getContext("2d");
    if (measureCtx) measureCtx.font = FONT;
  }
  return measureCtx ? measureCtx.measureText(text).width : text.length * 7;
}

export function nodeSize(label: string, kind: NodeKind): { w: number; h: number; label: string } {
  let text = label;
  let width = measure(text);
  const max = 200;
  if (width > max) {
    while (text.length > 3 && measure(text + "…") > max) text = text.slice(0, -1);
    text += "…";
    width = measure(text);
  }
  const pad = kind === "Property" || kind === "ExternalProperty" ? 18 : kind === "IfcReference" ? 22 : 16;
  return { w: Math.ceil(width + pad), h: kind === "Property" || kind === "ExternalProperty" ? 22 : 26, label: text };
}

// ------------------------------------------------------------------ geometry

function clipRect(cx: number, cy: number, w: number, h: number, tx: number, ty: number): [number, number] {
  const dx = tx - cx;
  const dy = ty - cy;
  if (dx === 0 && dy === 0) return [cx, cy];
  const sx = dx !== 0 ? w / 2 / Math.abs(dx) : Infinity;
  const sy = dy !== 0 ? h / 2 / Math.abs(dy) : Infinity;
  const s = Math.min(sx, sy, 1);
  return [cx + dx * s, cy + dy * s];
}

export function edgeGeometry(a: RNode, b: RNode, routing: Routing, lane: number, lanes: number): Geometry {
  const offset = (lane - (lanes - 1) / 2) * 26;
  if (routing === "orthogonal") {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const horizontal = Math.abs(dx) - (a.w + b.w) / 2 > Math.abs(dy) - (a.h + b.h) / 2;
    if (horizontal) {
      const sgn = Math.sign(dx) || 1;
      const sx = a.x + (sgn * a.w) / 2;
      const ex = b.x - (sgn * b.w) / 2;
      const mx = (sx + ex) / 2 + offset * 0.5;
      const sy = a.y + offset * 0.15;
      const ey = b.y + offset * 0.15;
      return { type: "poly", pts: [sx, sy, mx, sy, mx, ey, ex, ey] };
    }
    const sgn = Math.sign(dy) || 1;
    const sy = a.y + (sgn * a.h) / 2;
    const ey = b.y - (sgn * b.h) / 2;
    const my = (sy + ey) / 2 + offset * 0.5;
    const sx = a.x + offset * 0.15;
    const ex = b.x + offset * 0.15;
    return { type: "poly", pts: [sx, sy, sx, my, ex, my, ex, ey] };
  }
  if (routing === "straight" && lanes <= 1) {
    const [x0, y0] = clipRect(a.x, a.y, a.w, a.h, b.x, b.y);
    const [x1, y1] = clipRect(b.x, b.y, b.w, b.h, a.x, a.y);
    return { type: "poly", pts: [x0, y0, x1, y1] };
  }
  // curved (also used for parallel edges in straight mode)
  const mx = (a.x + b.x) / 2;
  const my = (a.y + b.y) / 2;
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const len = Math.hypot(dx, dy) || 1;
  const bend = routing === "curved" ? offset + len * 0.12 : offset;
  const cx = mx + (-dy / len) * bend;
  const cy = my + (dx / len) * bend;
  const [x0, y0] = clipRect(a.x, a.y, a.w, a.h, cx, cy);
  const [x1, y1] = clipRect(b.x, b.y, b.w, b.h, cx, cy);
  return { type: "quad", pts: [x0, y0, cx, cy, x1, y1] };
}

function endDirection(g: Geometry): [number, number, number, number] {
  const p = g.pts;
  const n = p.length;
  const ex = p[n - 2];
  const ey = p[n - 1];
  let px = p[n - 4];
  let py = p[n - 3];
  if (px === ex && py === ey && n >= 6) {
    px = p[n - 6];
    py = p[n - 5];
  }
  return [px, py, ex, ey];
}

function midpoint(g: Geometry): [number, number] {
  const p = g.pts;
  if (g.type === "quad") return [0.25 * p[0] + 0.5 * p[2] + 0.25 * p[4], 0.25 * p[1] + 0.5 * p[3] + 0.25 * p[5]];
  if (p.length === 8) return [(p[2] + p[4]) / 2, (p[3] + p[5]) / 2];
  return [(p[0] + p[2]) / 2, (p[1] + p[3]) / 2];
}

function addPath(ctx: CanvasRenderingContext2D | Path2D, g: Geometry) {
  const p = g.pts;
  ctx.moveTo(p[0], p[1]);
  if (g.type === "quad") ctx.quadraticCurveTo(p[2], p[3], p[4], p[5]);
  else for (let i = 2; i < p.length; i += 2) ctx.lineTo(p[i], p[i + 1]);
}

function addArrow(ctx: CanvasRenderingContext2D, g: Geometry, size: number) {
  const [px, py, ex, ey] = endDirection(g);
  const a = Math.atan2(ey - py, ex - px);
  ctx.moveTo(ex, ey);
  ctx.lineTo(ex - size * Math.cos(a - 0.4), ey - size * Math.sin(a - 0.4));
  ctx.lineTo(ex - size * Math.cos(a + 0.4), ey - size * Math.sin(a + 0.4));
  ctx.closePath();
}

function shapePath(ctx: CanvasRenderingContext2D | Path2D, n: RNode) {
  const shape = NODE_STYLE[n.kind].shape;
  const x = n.x - n.w / 2;
  const y = n.y - n.h / 2;
  if (shape === "rect") {
    ctx.rect(x, y, n.w, n.h);
  } else if (shape === "pill" || shape === "round") {
    const r = shape === "pill" ? n.h / 2 : 6;
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + n.w, y, x + n.w, y + n.h, r);
    ctx.arcTo(x + n.w, y + n.h, x, y + n.h, r);
    ctx.arcTo(x, y + n.h, x, y, r);
    ctx.arcTo(x, y, x + n.w, y, r);
    ctx.closePath();
  } else {
    const c = 9;
    ctx.moveTo(x + c, y);
    ctx.lineTo(x + n.w - c, y);
    ctx.lineTo(x + n.w, n.y);
    ctx.lineTo(x + n.w - c, y + n.h);
    ctx.lineTo(x + c, y + n.h);
    ctx.lineTo(x, n.y);
    ctx.closePath();
  }
}

// ------------------------------------------------------------------ drawing

export function draw(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  dpr: number,
  view: View,
  nodes: RNode[],
  edges: REdge[],
  opts: DrawOptions,
  overlay: Overlay,
) {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = opts.dark ? "#1a1b1e" : "#ffffff";
  ctx.fillRect(0, 0, width, height);
  ctx.setTransform(dpr * view.k, 0, 0, dpr * view.k, dpr * view.x, dpr * view.y);

  // visible world rectangle
  const vx0 = -view.x / view.k - 50;
  const vy0 = -view.y / view.k - 50;
  const vx1 = (width - view.x) / view.k + 50;
  const vy1 = (height - view.y) / view.k + 50;
  const visible = (n: RNode) => n.x + n.w / 2 > vx0 && n.x - n.w / 2 < vx1 && n.y + n.h / 2 > vy0 && n.y - n.h / 2 < vy1;
  const detail = view.k >= 0.45;
  const dimming = overlay.highlight !== null;

  const drawEdges = (subset: (e: REdge, i: number) => boolean, alpha: number) => {
    ctx.globalAlpha = alpha;
    const byKind = new Map<EdgeKind, number[]>();
    edges.forEach((e, i) => {
      if (!subset(e, i)) return;
      const a = nodes[e.s];
      const b = nodes[e.t];
      if (!a || !b) return;
      if ((a.x < vx0 && b.x < vx0) || (a.x > vx1 && b.x > vx1) || (a.y < vy0 && b.y < vy0) || (a.y > vy1 && b.y > vy1)) return;
      if (!byKind.has(e.kind)) byKind.set(e.kind, []);
      byKind.get(e.kind)!.push(i);
    });
    for (const [kind, list] of byKind) {
      const style = EDGE_STYLE[kind];
      ctx.strokeStyle = style.color;
      ctx.fillStyle = style.color;
      ctx.lineWidth = Math.max(style.width, 0.8 / view.k);
      ctx.setLineDash(detail ? style.dash : []);
      ctx.beginPath();
      const geoms: Geometry[] = [];
      for (const i of list) {
        const e = edges[i];
        const g = edgeGeometry(nodes[e.s], nodes[e.t], opts.routing, e.lane, e.lanes);
        geoms.push(g);
        addPath(ctx, g);
      }
      ctx.stroke();
      if (opts.arrows && detail) {
        ctx.setLineDash([]);
        ctx.beginPath();
        for (const g of geoms) addArrow(ctx, g, 9);
        ctx.fill();
      }
      if (opts.edgeLabels && view.k > 0.8) {
        ctx.font = "10px Inter, system-ui, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "bottom";
        ctx.fillStyle = opts.dark ? "#adb5bd" : "#495057";
        list.forEach((i, j) => {
          const [mx, my] = midpoint(geoms[j]);
          if (edges[i].label) ctx.fillText(edges[i].label, mx, my - 2);
        });
      }
    }
    ctx.setLineDash([]);
  };

  if (dimming) {
    const hl = overlay.highlight!;
    drawEdges((e) => !(hl.has(e.s) && hl.has(e.t)), 0.15);
    drawEdges((e) => hl.has(e.s) && hl.has(e.t), 1);
  } else drawEdges(() => true, 1);

  // selected edge on top
  if (overlay.selectedEdge !== null && edges[overlay.selectedEdge]) {
    const e = edges[overlay.selectedEdge];
    const g = edgeGeometry(nodes[e.s], nodes[e.t], opts.routing, e.lane, e.lanes);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = "#fab005";
    ctx.lineWidth = 4 / Math.max(view.k, 0.5);
    ctx.beginPath();
    addPath(ctx, g);
    ctx.stroke();
  }

  // nodes, batched by kind
  const drawNodes = (subset: (i: number) => boolean, alpha: number) => {
    ctx.globalAlpha = alpha;
    const byKind = new Map<NodeKind, number[]>();
    nodes.forEach((n, i) => {
      if (!subset(i) || !visible(n)) return;
      if (!byKind.has(n.kind)) byKind.set(n.kind, []);
      byKind.get(n.kind)!.push(i);
    });
    for (const [kind, list] of byKind) {
      const style = NODE_STYLE[kind];
      ctx.beginPath();
      for (const i of list) {
        if (detail) shapePath(ctx, nodes[i]);
        else ctx.rect(nodes[i].x - nodes[i].w / 2, nodes[i].y - nodes[i].h / 2, nodes[i].w, nodes[i].h);
      }
      if (style.dashed) {
        ctx.fillStyle = opts.dark ? "#25262b" : "#fff";
        ctx.fill();
        ctx.strokeStyle = style.color;
        ctx.lineWidth = 2;
        ctx.setLineDash(detail ? [5, 3] : []);
        ctx.stroke();
        ctx.setLineDash([]);
      } else {
        ctx.fillStyle = style.color;
        ctx.fill();
        if (kind === "GroupOfProperties" && detail) {
          ctx.strokeStyle = opts.dark ? "#e5dbff" : "#3b2a8a";
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      }
      if (opts.labels && view.k >= 0.4) {
        ctx.font = FONT;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = style.dashed ? (opts.dark ? "#e9ecef" : "#212529") : "#ffffff";
        for (const i of list) ctx.fillText(nodes[i].label, nodes[i].x, nodes[i].y + 0.5);
      }
    }
  };
  if (dimming) {
    const hl = overlay.highlight!;
    drawNodes((i) => !hl.has(i), 0.2);
    drawNodes((i) => hl.has(i), 1);
  } else drawNodes(() => true, 1);
  ctx.globalAlpha = 1;

  // pins, selection and hover outlines
  ctx.lineWidth = 2.5 / Math.max(view.k, 0.6);
  for (const i of overlay.selectedNodes) {
    const n = nodes[i];
    if (!n || !visible(n)) continue;
    ctx.strokeStyle = "#fab005";
    ctx.beginPath();
    ctx.rect(n.x - n.w / 2 - 3, n.y - n.h / 2 - 3, n.w + 6, n.h + 6);
    ctx.stroke();
  }
  if (overlay.hover !== null && nodes[overlay.hover]) {
    const n = nodes[overlay.hover];
    ctx.strokeStyle = opts.dark ? "#ffffff" : "#000000";
    ctx.lineWidth = 1.5 / view.k;
    ctx.beginPath();
    shapePath(ctx, n);
    ctx.stroke();
  }
  if (detail) {
    ctx.fillStyle = opts.dark ? "#ffffff" : "#212529";
    for (const n of nodes) {
      if (!n.fixed || !visible(n)) continue;
      ctx.beginPath();
      ctx.arc(n.x + n.w / 2 - 1, n.y - n.h / 2 + 1, 3, 0, Math.PI * 2);
      ctx.fill();
    }
  }
  if (overlay.connectLine) {
    const l = overlay.connectLine;
    ctx.strokeStyle = "#fab005";
    ctx.lineWidth = 2 / view.k;
    ctx.setLineDash([6 / view.k, 4 / view.k]);
    ctx.beginPath();
    ctx.moveTo(l.x1, l.y1);
    ctx.lineTo(l.x2, l.y2);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  if (overlay.box) {
    const b = overlay.box;
    ctx.fillStyle = "rgba(34,139,230,0.12)";
    ctx.strokeStyle = "#228be6";
    ctx.lineWidth = 1 / view.k;
    ctx.fillRect(Math.min(b.x1, b.x2), Math.min(b.y1, b.y2), Math.abs(b.x2 - b.x1), Math.abs(b.y2 - b.y1));
    ctx.strokeRect(Math.min(b.x1, b.x2), Math.min(b.y1, b.y2), Math.abs(b.x2 - b.x1), Math.abs(b.y2 - b.y1));
  }
}

// ------------------------------------------------------------------ hit testing

export function hitNode(nodes: RNode[], x: number, y: number): number | null {
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i];
    if (Math.abs(x - n.x) <= n.w / 2 && Math.abs(y - n.y) <= n.h / 2) return i;
  }
  return null;
}

function distSeg(px: number, py: number, x0: number, y0: number, x1: number, y1: number) {
  const dx = x1 - x0;
  const dy = y1 - y0;
  const l2 = dx * dx + dy * dy;
  let t = l2 ? ((px - x0) * dx + (py - y0) * dy) / l2 : 0;
  t = Math.max(0, Math.min(1, t));
  return Math.hypot(px - (x0 + t * dx), py - (y0 + t * dy));
}

export function hitEdge(nodes: RNode[], edges: REdge[], routing: Routing, x: number, y: number, tol: number): number | null {
  let best: number | null = null;
  let bestD = tol;
  edges.forEach((e, i) => {
    const a = nodes[e.s];
    const b = nodes[e.t];
    if (!a || !b) return;
    const g = edgeGeometry(a, b, routing, e.lane, e.lanes);
    let pts = g.pts;
    if (g.type === "quad") {
      const s: number[] = [];
      for (let k = 0; k <= 12; k++) {
        const t = k / 12;
        const u = 1 - t;
        s.push(u * u * pts[0] + 2 * u * t * pts[2] + t * t * pts[4], u * u * pts[1] + 2 * u * t * pts[3] + t * t * pts[5]);
      }
      pts = s;
    }
    for (let k = 0; k + 3 < pts.length; k += 2) {
      const d = distSeg(x, y, pts[k], pts[k + 1], pts[k + 2], pts[k + 3]);
      if (d < bestD) {
        bestD = d;
        best = i;
      }
    }
  });
  return best;
}

export function bounds(nodes: RNode[]): { x0: number; y0: number; x1: number; y1: number } {
  let x0 = Infinity,
    y0 = Infinity,
    x1 = -Infinity,
    y1 = -Infinity;
  for (const n of nodes) {
    x0 = Math.min(x0, n.x - n.w / 2);
    y0 = Math.min(y0, n.y - n.h / 2);
    x1 = Math.max(x1, n.x + n.w / 2);
    y1 = Math.max(y1, n.y + n.h / 2);
  }
  if (!isFinite(x0)) return { x0: -100, y0: -100, x1: 100, y1: 100 };
  return { x0, y0, x1, y1 };
}

// ------------------------------------------------------------------ SVG export

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function svgShape(n: RNode): string {
  const p = new SvgPath();
  shapePath(p as unknown as CanvasRenderingContext2D, n);
  return p.d;
}

/** Minimal path recorder implementing the canvas path API used above. */
class SvgPath {
  d = "";
  private f(n: number) {
    return Math.round(n * 100) / 100;
  }
  moveTo(x: number, y: number) {
    this.d += `M${this.f(x)} ${this.f(y)}`;
  }
  lineTo(x: number, y: number) {
    this.d += `L${this.f(x)} ${this.f(y)}`;
  }
  quadraticCurveTo(cx: number, cy: number, x: number, y: number) {
    this.d += `Q${this.f(cx)} ${this.f(cy)} ${this.f(x)} ${this.f(y)}`;
  }
  rect(x: number, y: number, w: number, h: number) {
    this.d += `M${this.f(x)} ${this.f(y)}h${this.f(w)}v${this.f(h)}h${this.f(-w)}Z`;
  }
  arcTo(x1: number, y1: number, x2: number, y2: number, r: number) {
    // approximate rounded corner: line towards corner then quadratic to the next edge
    const lastMatch = /(-?[\d.]+) (-?[\d.]+)$/.exec(this.d);
    const x0 = lastMatch ? Number(lastMatch[1]) : x1;
    const y0 = lastMatch ? Number(lastMatch[2]) : y1;
    const d1 = Math.hypot(x1 - x0, y1 - y0) || 1;
    const d2 = Math.hypot(x2 - x1, y2 - y1) || 1;
    const ax = x1 - ((x1 - x0) / d1) * r;
    const ay = y1 - ((y1 - y0) / d1) * r;
    const bx = x1 + ((x2 - x1) / d2) * r;
    const by = y1 + ((y2 - y1) / d2) * r;
    this.lineTo(ax, ay);
    this.quadraticCurveTo(x1, y1, bx, by);
  }
  closePath() {
    this.d += "Z";
  }
}

export function toSvg(nodes: RNode[], edges: REdge[], opts: DrawOptions, infos?: Record<string, Record<string, string>>): { svg: string; width: number; height: number } {
  const b = bounds(nodes);
  const pad = 40;
  const w = b.x1 - b.x0 + 2 * pad;
  const h = b.y1 - b.y0 + 2 * pad;
  const parts: string[] = [];
  parts.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${b.x0 - pad} ${b.y0 - pad} ${w} ${h}" width="${Math.round(w)}" height="${Math.round(h)}" font-family="Inter, system-ui, sans-serif" font-size="12">`);
  parts.push(`<rect x="${b.x0 - pad}" y="${b.y0 - pad}" width="${w}" height="${h}" fill="${opts.dark ? "#1a1b1e" : "#ffffff"}"/>`);
  parts.push('<g class="edges">');
  for (const e of edges) {
    const a = nodes[e.s];
    const t = nodes[e.t];
    if (!a || !t) continue;
    const style = EDGE_STYLE[e.kind];
    const g = edgeGeometry(a, t, opts.routing, e.lane, e.lanes);
    const p = new SvgPath();
    addPath(p as unknown as CanvasRenderingContext2D, g);
    const dash = style.dash.length ? ` stroke-dasharray="${style.dash.join(" ")}"` : "";
    parts.push(`<path d="${p.d}" fill="none" stroke="${style.color}" stroke-width="${style.width}"${dash}><title>${esc(e.label || e.kind)}</title></path>`);
    if (opts.arrows) {
      const [px, py, ex, ey] = endDirection(g);
      const ang = Math.atan2(ey - py, ex - px);
      const s = 9;
      parts.push(
        `<path d="M${ex} ${ey}L${ex - s * Math.cos(ang - 0.4)} ${ey - s * Math.sin(ang - 0.4)}L${ex - s * Math.cos(ang + 0.4)} ${ey - s * Math.sin(ang + 0.4)}Z" fill="${style.color}"/>`,
      );
    }
    if (opts.edgeLabels && e.label) {
      const [mx, my] = midpoint(g);
      parts.push(`<text x="${mx}" y="${my - 3}" text-anchor="middle" font-size="10" fill="#495057">${esc(e.label)}</text>`);
    }
  }
  parts.push("</g><g class=\"nodes\">");
  for (const n of nodes) {
    const style = NODE_STYLE[n.kind];
    const info = infos?.[n.id];
    const data = info ? ` data-info="${esc(JSON.stringify(info))}"` : "";
    const fill = style.dashed ? (opts.dark ? "#25262b" : "#ffffff") : style.color;
    const stroke = style.dashed ? ` stroke="${style.color}" stroke-width="2" stroke-dasharray="5 3"` : "";
    const textColor = style.dashed ? (opts.dark ? "#e9ecef" : "#212529") : "#ffffff";
    parts.push(
      `<g class="node" data-id="${esc(n.id)}"${data}><path d="${svgShape(n)}" fill="${fill}"${stroke}/>` +
        (opts.labels ? `<text x="${n.x}" y="${n.y + 4}" text-anchor="middle" fill="${textColor}">${esc(n.label)}</text>` : "") +
        `<title>${esc(n.label)}</title></g>`,
    );
  }
  parts.push("</g></svg>");
  return { svg: parts.join(""), width: w, height: h };
}


/** Render edges with lane indices for parallel edges between the same node pair. */
export function redgesFrom(edges: GEdge[], indexOf: Map<string, number>): REdge[] {
  const pairCount = new Map<string, number>();
  const out: REdge[] = [];
  for (const e of edges) {
    const s = indexOf.get(e.source);
    const tt = indexOf.get(e.target);
    if (s === undefined || tt === undefined) continue;
    const key = s < tt ? `${s}-${tt}` : `${tt}-${s}`;
    const lane = pairCount.get(key) ?? 0;
    pairCount.set(key, lane + 1);
    out.push({ id: e.id, s, t: tt, kind: e.kind, label: e.label, lane, lanes: 1 });
  }
  for (const e of out) {
    const key = e.s < e.t ? `${e.s}-${e.t}` : `${e.t}-${e.s}`;
    e.lanes = pairCount.get(key) ?? 1;
    if (e.s > e.t) e.lane = e.lanes - 1 - e.lane; // keep opposite directions on different sides
  }
  return out;
}
