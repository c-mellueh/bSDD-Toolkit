/**
 * Standalone interactive HTML export of graphs (works offline, no external resources).
 *
 * Mirrors the desktop graph viewer's HTML export: the page holds one graph per tab,
 * a legend, and a details panel that shows the definition and the class properties of
 * the clicked node. Double-clicking a node opens it in bSDD (version replaced by
 * "latest" so links keep working after new releases).
 */
import { GOP, classUri, cpName, descendants, propertyUri, resolveProperty, type Indexes } from "../model";
import type { Doc } from "../types";
import { treeLayout } from "./layout";
import { EDGE_STYLE, NODE_STYLE, describeNode, edgesBetween, type EdgeKind, type GNode, type NodeKind } from "./model";
import { nodeSize, redgesFrom, toSvg, type DrawOptions, type RNode } from "./renderer";

export interface HtmlTab {
  title: string;
  nodes: RNode[];
  kinds: { nodes: NodeKind[]; edges: EdgeKind[] };
  svg: string;
  info: Record<string, NodeInfo>;
}

interface NodeInfo {
  name: string;
  kind: string;
  code: string;
  definition: string;
  url: string | null;
  rows: string[][]; // class properties: name, property set, datatype, description
}

const latest = (doc: Doc, uri: string) => (doc.dictionary.DictionaryVersion ? uri.replace(`/${doc.dictionary.DictionaryVersion}/`, "/latest/") : uri);

function nodeInfo(doc: Doc, idx: Indexes, n: GNode): NodeInfo {
  const d = doc.dictionary;
  const base = { name: n.label, kind: n.kind, code: n.code ?? "", definition: "", url: null as string | null, rows: [] as string[][] };
  if (n.kind === "Class" || n.kind === "GroupOfProperties") {
    const c = idx.classes.get(n.code ?? "");
    if (!c) return base;
    const rows = (c.ClassProperties ?? [])
      .map((cp) => {
        const p = resolveProperty(idx, d, cp);
        return [cpName(idx, d, cp), cp.PropertySet ?? "", p?.DataType ?? "", cp.Description ?? p?.Description ?? ""];
      })
      .sort((a, b) => a[1].localeCompare(b[1]) || a[0].localeCompare(b[0]));
    return { ...base, definition: c.Definition || c.Description || "", url: latest(doc, c.OwnedUri || classUri(d, c.Code)), rows };
  }
  if (n.kind === "Property") {
    const p = idx.properties.get(n.code ?? "");
    if (!p) return base;
    return { ...base, definition: p.Definition || p.Description || "", url: latest(doc, p.OwnedUri || propertyUri(d, p.Code)) };
  }
  if (n.uri) return { ...base, url: n.uri };
  return base;
}

/** Build one tab from graph nodes that already have positions. */
export function buildTab(doc: Doc, idx: Indexes, title: string, gnodes: GNode[], nodes: RNode[], gedges: Parameters<typeof redgesFrom>[0], opts: DrawOptions): HtmlTab {
  const indexOf = new Map(nodes.map((n, i) => [n.id, i]));
  const { svg } = toSvg(nodes, redgesFrom(gedges, indexOf), { ...opts, dark: false });
  const info: Record<string, NodeInfo> = {};
  for (const n of gnodes) info[n.id] = nodeInfo(doc, idx, n);
  return {
    title,
    nodes,
    svg,
    info,
    kinds: { nodes: [...new Set(gnodes.map((n) => n.kind))], edges: [...new Set(gedges.map((e) => e.kind))] },
  };
}

/** One tab per root class, each with its whole subtree laid out as a tree (desktop "Export Full HTML (Tabs)"). */
export function rootClassTabs(doc: Doc, idx: Indexes, opts: DrawOptions, hiddenEdges: Set<EdgeKind>): HtmlTab[] {
  const classes = (doc.dictionary.Classes ?? []).filter((c) => (c.ClassType ?? "Class") === "Class");
  const roots = classes.filter((c) => !c.ParentClassCode || !idx.classes.has(c.ParentClassCode));
  const tabs: HtmlTab[] = [];
  for (const root of roots) {
    const codes = [root.Code, ...descendants(idx, root.Code).filter((c) => idx.classes.get(c)?.ClassType !== GOP)];
    const ids = codes.map((c) => `c:${c}`);
    const gnodes = ids.map((id) => describeNode(doc, idx, id)).filter((n): n is GNode => !!n);
    const sized = gnodes.map((n) => ({ ...n, ...nodeSize(n.label, n.kind) }));
    // like the desktop export: the tabs show the class hierarchy only
    const gedges = edgesBetween(doc, idx, new Set(ids)).filter((e) => e.kind === "ParentClassCode" && !hiddenEdges.has(e.kind));
    const pos = treeLayout(sized.map((n) => ({ id: n.id, w: n.w, h: n.h })), gedges, "TB");
    const nodes: RNode[] = sized.map((n) => ({ id: n.id, kind: n.kind, label: n.label, x: pos.get(n.id)?.x ?? 0, y: pos.get(n.id)?.y ?? 0, w: n.w, h: n.h, fixed: false }));
    tabs.push(buildTab(doc, idx, root.Name || root.Code, gnodes, nodes, gedges, opts));
  }
  return tabs;
}

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

function legend(kinds: HtmlTab["kinds"]): string {
  const n = kinds.nodes
    .map((k) => {
      const st = NODE_STYLE[k];
      const box = st.dashed ? `border:2px dashed ${st.color};background:transparent` : `background:${st.color}`;
      return `<div class="lg-row"><span class="lg-node" style="${box}"></span>${esc(k)}</div>`;
    })
    .join("");
  const e = kinds.edges
    .map((k) => {
      const st = EDGE_STYLE[k];
      return `<div class="lg-row"><svg width="30" height="10"><line x1="1" y1="5" x2="29" y2="5" stroke="${st.color}" stroke-width="2" stroke-dasharray="${st.dash.join(" ")}"/></svg>${esc(k)}</div>`;
    })
    .join("");
  return `<div class="lg-title">Node types</div>${n}${e ? `<div class="lg-title">Relationship types</div>${e}` : ""}`;
}

/** Compose the full page. A tab bar is shown when there is more than one tab. */
export function htmlPage(doc: Doc, tabs: HtmlTab[], dark = false): string {
  const d = doc.dictionary;
  const dictTitle = `${d.OrganizationCode}/${d.DictionaryCode} v${d.DictionaryVersion}`;
  const pageTitle = `${d.DictionaryName || d.DictionaryCode} – bSDD graph`;
  const tabBar =
    tabs.length > 1
      ? `<nav class="tabs">${tabs.map((t, i) => `<button class="tab${i === 0 ? " active" : ""}" data-tab="${i}">${esc(t.title || `Graph ${i + 1}`)}<span class="count">${t.nodes.length}</span></button>`).join("")}</nav>`
      : "";
  const sections = tabs
    .map(
      (t, i) => `<section class="graph-section${i === 0 ? " active" : ""}" data-tab="${i}">
  <div class="graph-area">
    <div class="graph-wrap">${t.svg}</div>
    <div class="legend">${legend(t.kinds)}</div>
    <div class="tools"><button class="fit" title="Fit">⤢</button><button class="zin" title="Zoom in">+</button><button class="zout" title="Zoom out">−</button></div>
  </div>
  <aside class="details">
    <div class="card"><div class="d-head"><h3 class="d-name">Definition</h3><span class="d-kind" hidden></span></div>
      <div class="d-code"></div><p class="d-text empty">Click a class or property to see its definition. Double-click opens it in bSDD.</p>
      <a class="d-link" target="_blank" rel="noreferrer" hidden>Open in bSDD ↗</a></div>
    <div class="card"><h3 class="p-title">Class properties</h3>
      <table class="props"><thead><tr><th>Property</th><th>Property set</th><th>Data type</th><th>Description</th></tr></thead>
      <tbody><tr><td class="empty" colspan="4">Select a class to view its properties.</td></tr></tbody></table></div>
  </aside>
  <script type="application/json" class="node-info">${JSON.stringify(t.info).replace(/</g, "\\u003c")}</script>
</section>`,
    )
    .join("\n");

  return `<!doctype html>
<html lang="en" data-theme="${dark ? "dark" : "light"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(pageTitle)}</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--text:#1f2328;--dim:#6b7280;--border:#dde1e6;--accent:#228be6;--accent-l:#e7f1fd;--graph:#ffffff;--overlay:rgba(255,255,255,.94)}
[data-theme=dark]{--bg:#141517;--card:#1f2023;--text:#e6e8eb;--dim:#9aa0a6;--border:#33363b;--accent:#4dabf7;--accent-l:#1c3047;--graph:#1a1b1e;--overlay:rgba(31,32,35,.94)}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--text);font:14px/1.45 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;min-height:100vh}
header{padding:14px 20px 0;display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
header h1{margin:0;font-size:20px}header .sub{color:var(--dim);font-size:13px}
.theme{flex:none;display:flex;align-items:center;gap:6px;border:1px solid var(--border);background:var(--card);color:var(--text);border-radius:20px;padding:5px 12px;font:inherit;font-size:13px;cursor:pointer}
.theme:hover{border-color:var(--accent)}
.tabs{display:flex;gap:4px;overflow-x:auto;padding:12px 20px 0;border-bottom:1px solid var(--border)}
.tab{background:none;border:none;border-bottom:2px solid transparent;color:var(--dim);padding:8px 12px;font:inherit;cursor:pointer;white-space:nowrap}
.tab:hover{color:var(--text)}.tab.active{color:var(--accent);border-bottom-color:var(--accent);font-weight:600}
.tab .count{margin-left:6px;font-size:11px;background:var(--accent-l);color:var(--accent);border-radius:10px;padding:1px 7px}
.graph-section{display:none;padding:16px 20px 24px}
.graph-section.active{display:block}
.graph-area{height:68vh;min-height:360px;position:relative;background:var(--graph);border:1px solid var(--border);border-radius:10px;overflow:hidden}
.graph-wrap,.graph-wrap svg{width:100%;height:100%;display:block}.graph-wrap{cursor:grab}.graph-wrap.drag{cursor:grabbing}
.svg-bg{fill:var(--graph)}
.node{cursor:pointer}.node:hover .node-shape{filter:brightness(1.12)}.node.selected .node-shape{stroke:var(--text);stroke-width:3}
.node.dashed .node-shape{fill:var(--graph)}.node.dashed .node-label{fill:var(--text)}.edge-label{fill:var(--dim)}
.legend{position:absolute;left:10px;top:10px;background:var(--overlay);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:8px 10px;font-size:12px;max-height:calc(100% - 20px);overflow:auto}
.lg-title{font-size:10px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);margin:4px 0}
.lg-row{display:flex;align-items:center;gap:8px;margin:2px 0}.lg-node{display:inline-block;width:16px;height:10px;border-radius:3px}
.tools{position:absolute;right:10px;top:10px;display:flex;flex-direction:column;gap:4px}
.tools button{width:30px;height:30px;border:1px solid var(--border);background:var(--card);color:var(--text);border-radius:6px;cursor:pointer;font-size:15px}
.details{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,2fr);gap:12px;margin-top:12px;align-items:start}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px}
.card h3{margin:0;font-size:15px}.d-head{display:flex;align-items:center;gap:8px}
.d-kind{font-size:10px;text-transform:uppercase;letter-spacing:.06em;background:var(--accent-l);color:var(--accent);border-radius:4px;padding:2px 6px}
.d-code{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim);margin-top:2px}
.d-text{margin:8px 0 0;white-space:pre-wrap}.empty{color:var(--dim);font-style:italic}
.d-link{display:inline-block;margin-top:10px;color:var(--accent);text-decoration:none;font-size:13px}
.props{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
.props th{text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--dim);padding:6px;border-bottom:1px solid var(--border)}
.props td{padding:6px;border-bottom:1px solid var(--border);vertical-align:top}.props tr:hover td{background:var(--accent-l)}
@media (max-width:900px){.details{grid-template-columns:minmax(0,1fr)}.graph-area{height:60vh}}
</style></head>
<body>
<header><div><h1>${esc(d.DictionaryName || d.DictionaryCode)}</h1><div class="sub">bSDD graph · ${esc(dictTitle)}</div></div>
<button class="theme" type="button" title="Day / night mode"><span class="theme-icon"></span><span class="theme-label"></span></button></header>
${tabBar}
${sections}
<script>
(function(){
  var root=document.documentElement,btn=document.querySelector('.theme');
  function setTheme(t){root.setAttribute('data-theme',t);btn.querySelector('.theme-icon').textContent=t==='dark'?'\u2600':'\u263E';btn.querySelector('.theme-label').textContent=t==='dark'?'Day':'Night';try{localStorage.setItem('bsdd-graph-theme',t)}catch(e){}}
  var saved=null;try{saved=localStorage.getItem('bsdd-graph-theme')}catch(e){}
  setTheme(saved||root.getAttribute('data-theme'));
  btn.addEventListener('click',function(){setTheme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  var tabs=[].slice.call(document.querySelectorAll('.tab')),secs=[].slice.call(document.querySelectorAll('.graph-section'));
  var inits={};
  function show(i){tabs.forEach(function(t){t.classList.toggle('active',t.dataset.tab==i)});secs.forEach(function(s){s.classList.toggle('active',s.dataset.tab==i)});init(secs[i]);}
  tabs.forEach(function(t){t.addEventListener('click',function(){show(+t.dataset.tab)})});
  function init(sec){
    if(!sec||inits[sec.dataset.tab])return;inits[sec.dataset.tab]=1;
    var info={};try{info=JSON.parse(sec.querySelector('.node-info').textContent)}catch(e){}
    var wrap=sec.querySelector('.graph-wrap'),svg=wrap.querySelector('svg');svg.removeAttribute('width');svg.removeAttribute('height');
    var full=svg.getAttribute('viewBox').split(' ').map(Number),vb=full.slice();
    function apply(){svg.setAttribute('viewBox',vb.join(' '))}
    function fit(){var r=wrap.getBoundingClientRect(),a=r.width/r.height,w=full[2],h=full[3];if(w/h>a){h=w/a}else{w=h*a}vb=[full[0]-(w-full[2])/2,full[1]-(h-full[3])/2,w,h];apply()}
    function zoom(f,cx,cy){var r=wrap.getBoundingClientRect();if(cx===undefined){cx=r.left+r.width/2;cy=r.top+r.height/2}var mx=vb[0]+(cx-r.left)/r.width*vb[2],my=vb[1]+(cy-r.top)/r.height*vb[3];vb[2]*=f;vb[3]*=f;vb[0]=mx-(mx-vb[0])*f;vb[1]=my-(my-vb[1])*f;apply()}
    fit();window.addEventListener('resize',fit);
    sec.querySelector('.fit').onclick=fit;sec.querySelector('.zin').onclick=function(){zoom(1/1.25)};sec.querySelector('.zout').onclick=function(){zoom(1.25)};
    wrap.addEventListener('wheel',function(e){e.preventDefault();zoom(Math.exp(e.deltaY*0.0015),e.clientX,e.clientY)},{passive:false});
    var drag=null,moved=false;
    wrap.addEventListener('pointerdown',function(e){drag={x:e.clientX,y:e.clientY,v:vb.slice()};moved=false;wrap.classList.add('drag')});
    window.addEventListener('pointermove',function(e){if(!drag)return;var r=wrap.getBoundingClientRect();if(Math.abs(e.clientX-drag.x)+Math.abs(e.clientY-drag.y)>3)moved=true;vb[0]=drag.v[0]-(e.clientX-drag.x)/r.width*vb[2];vb[1]=drag.v[1]-(e.clientY-drag.y)/r.height*vb[3];apply()});
    window.addEventListener('pointerup',function(){drag=null;wrap.classList.remove('drag')});
    var name=sec.querySelector('.d-name'),kind=sec.querySelector('.d-kind'),code=sec.querySelector('.d-code'),text=sec.querySelector('.d-text'),link=sec.querySelector('.d-link'),ptitle=sec.querySelector('.p-title'),tbody=sec.querySelector('.props tbody');
    function empty(msg){tbody.innerHTML='';var tr=document.createElement('tr'),td=document.createElement('td');td.className='empty';td.colSpan=4;td.textContent=msg;tr.appendChild(td);tbody.appendChild(tr)}
    function render(d){
      name.textContent=d.name;kind.textContent=d.kind;kind.hidden=false;code.textContent=d.code||'';
      if(d.definition){text.textContent=d.definition;text.classList.remove('empty')}else{text.textContent='No definition available.';text.classList.add('empty')}
      if(d.url){link.href=d.url;link.hidden=false}else link.hidden=true;
      if(d.kind!=='Class'&&d.kind!=='GroupOfProperties'){ptitle.textContent='Class properties';empty('Select a class to view its properties.');return}
      ptitle.textContent='Class properties – '+d.name;
      if(!d.rows.length){empty('This class has no properties.');return}
      tbody.innerHTML='';d.rows.forEach(function(row){var tr=document.createElement('tr');row.forEach(function(c){var td=document.createElement('td');td.textContent=c||'';tr.appendChild(td)});tbody.appendChild(tr)});
    }
    var sel=null;
    [].slice.call(sec.querySelectorAll('.node')).forEach(function(el){
      el.addEventListener('click',function(){if(moved)return;if(sel)sel.classList.remove('selected');el.classList.add('selected');sel=el;var d=info[el.dataset.id];if(d)render(d)});
      el.addEventListener('dblclick',function(){var d=info[el.dataset.id];if(d&&d.url)window.open(d.url,'_blank')});
    });
  }
  show(0);
})();
</script>
</body></html>`;
}
