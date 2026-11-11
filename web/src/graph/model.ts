/** Graph model derived from the dictionary: node / edge types, ids and neighbourhoods. */
import { GOP, internalCode, isUri, resolveProperty, type Indexes } from "../model";
import type { Doc } from "../types";

export const NODE_KINDS = ["Class", "GroupOfProperties", "Property", "ExternalClass", "ExternalProperty", "IfcReference"] as const;
export type NodeKind = (typeof NODE_KINDS)[number];

export const EDGE_KINDS = [
  "ParentClassCode",
  "ClassProperty",
  "GopProperty",
  "IfcReference",
  "HasMaterial",
  "HasReference",
  "IsEqualTo",
  "IsSimilarTo",
  "IsParentOf",
  "IsChildOf",
  "HasPart",
  "IsPartOf",
] as const;
export type EdgeKind = (typeof EDGE_KINDS)[number];

export const NODE_STYLE: Record<NodeKind, { color: string; shape: "round" | "rect" | "pill" | "hex"; dashed?: boolean }> = {
  Class: { color: "#d9480f", shape: "round" },
  GroupOfProperties: { color: "#7048e8", shape: "rect" },
  Property: { color: "#1c7ed6", shape: "pill" },
  ExternalClass: { color: "#e8590c", shape: "round", dashed: true },
  ExternalProperty: { color: "#4dabf7", shape: "pill", dashed: true },
  IfcReference: { color: "#2b8a3e", shape: "hex" },
};

export const EDGE_STYLE: Record<EdgeKind, { color: string; dash: number[]; width: number }> = {
  ParentClassCode: { color: "#0ca678", dash: [2, 4], width: 1.6 },
  ClassProperty: { color: "#868e96", dash: [8, 3, 2, 3], width: 1.2 },
  GopProperty: { color: "#9775fa", dash: [8, 3, 2, 3], width: 1.2 },
  IfcReference: { color: "#40c057", dash: [6, 4], width: 1.2 },
  HasMaterial: { color: "#f08c00", dash: [], width: 1.6 },
  HasReference: { color: "#7950f2", dash: [], width: 1.6 },
  IsEqualTo: { color: "#e64980", dash: [], width: 1.8 },
  IsSimilarTo: { color: "#f783ac", dash: [5, 3], width: 1.6 },
  IsParentOf: { color: "#1098ad", dash: [], width: 1.6 },
  IsChildOf: { color: "#15aabf", dash: [5, 3], width: 1.6 },
  HasPart: { color: "#5c940d", dash: [], width: 1.6 },
  IsPartOf: { color: "#82c91e", dash: [5, 3], width: 1.6 },
};

/** Display name of an edge kind (untranslated i18n key). */
export const edgeKindLabel = (k: EdgeKind) => (k === "GopProperty" ? "ClassProperty (group of properties)" : k === "ClassProperty" ? "ClassProperty (class)" : k);

export type EdgeRef =
  | { type: "parent"; child: string }
  | { type: "classRelation"; owner: string; index: number }
  | { type: "propertyRelation"; owner: string; index: number }
  | { type: "classProperty"; owner: string; cpCode: string }
  | { type: "ifc"; owner: string; name: string };

export interface GNode {
  id: string;
  kind: NodeKind;
  label: string;
  code: string;
  uri?: string;
  info?: Record<string, string>;
}

export interface GEdge {
  id: string;
  source: string;
  target: string;
  kind: EdgeKind;
  label: string;
  ref: EdgeRef;
}

export const classId = (code: string) => `c:${code}`;
export const propId = (code: string) => `p:${code}`;

/** Normalise a node id for an arbitrary reference (class/property code, URI, IFC name). */
export function idForUri(doc: Doc, uri: string, kind: "class" | "prop"): string {
  const code = internalCode(doc.dictionary, uri, kind);
  if (code) return kind === "class" ? classId(code) : propId(code);
  return kind === "class" ? `xc:${uri}` : `xp:${uri}`;
}

function lastSegment(uri: string) {
  const parts = uri.split("/").filter(Boolean);
  return parts[parts.length - 1] ?? uri;
}

/** Labels for external nodes collected from relation names in the dictionary. */
function externalLabels(doc: Doc): Map<string, string> {
  const map = new Map<string, string>();
  for (const c of doc.dictionary.Classes ?? []) {
    for (const r of c.ClassRelations ?? []) if (r.RelatedClassName) map.set(`xc:${r.RelatedClassUri}`, r.RelatedClassName);
  }
  for (const p of doc.dictionary.Properties ?? []) {
    for (const r of p.PropertyRelations ?? []) if (r.RelatedPropertyName) map.set(`xp:${r.RelatedPropertyUri}`, r.RelatedPropertyName);
  }
  return map;
}

/** Describe a node id; returns null if it refers to an internal item that no longer exists. */
export function describeNode(doc: Doc, idx: Indexes, id: string, labels?: Map<string, string>): GNode | null {
  const [prefix, ...rest] = id.split(":");
  const key = rest.join(":");
  if (prefix === "c") {
    const c = idx.classes.get(key);
    if (!c) return null;
    return {
      id,
      kind: c.ClassType === GOP ? "GroupOfProperties" : "Class",
      label: c.Name,
      code: c.Code,
      info: { Code: c.Code, Type: c.ClassType ?? "Class", Definition: c.Definition ?? "", Status: c.Status ?? "" },
    };
  }
  if (prefix === "p") {
    const p = idx.properties.get(key);
    if (!p) return null;
    return { id, kind: "Property", label: p.Name, code: p.Code, info: { Code: p.Code, DataType: p.DataType ?? "", Definition: p.Definition ?? "", Units: (p.Units ?? []).join(", ") } };
  }
  if (prefix === "xc" || prefix === "xp") {
    const lbl = (labels ?? externalLabels(doc)).get(id) ?? lastSegment(key);
    return { id, kind: prefix === "xc" ? "ExternalClass" : "ExternalProperty", label: lbl, code: lastSegment(key), uri: key, info: { URI: key } };
  }
  if (prefix === "ifc") return { id, kind: "IfcReference", label: key, code: key, info: { Entity: key } };
  return null;
}

/** All edges between nodes of the given set. */
export function edgesBetween(doc: Doc, idx: Indexes, ids: Set<string>): GEdge[] {
  const d = doc.dictionary;
  const edges: GEdge[] = [];
  for (const id of ids) {
    if (id.startsWith("c:")) {
      const c = idx.classes.get(id.slice(2));
      if (!c) continue;
      if (c.ParentClassCode && ids.has(classId(c.ParentClassCode)))
        edges.push({ id: `pc:${c.Code}`, source: id, target: classId(c.ParentClassCode), kind: "ParentClassCode", label: "Parent", ref: { type: "parent", child: c.Code } });
      (c.ClassRelations ?? []).forEach((r, i) => {
        const target = idForUri(doc, r.RelatedClassUri, "class");
        if (!ids.has(target)) return;
        const kind = (EDGE_KINDS as readonly string[]).includes(r.RelationType) ? (r.RelationType as EdgeKind) : "HasReference";
        edges.push({ id: `cr:${c.Code}:${i}`, source: id, target, kind, label: r.RelationType, ref: { type: "classRelation", owner: c.Code, index: i } });
      });
      for (const cp of c.ClassProperties ?? []) {
        const p = resolveProperty(idx, d, cp);
        const target = p ? propId(p.Code) : cp.PropertyUri ? `xp:${cp.PropertyUri}` : null;
        if (!target || !ids.has(target)) continue;
        edges.push({ id: `cp:${c.Code}:${cp.Code}`, source: id, target, kind: c.ClassType === GOP ? "GopProperty" : "ClassProperty", label: cp.PropertySet ?? "", ref: { type: "classProperty", owner: c.Code, cpCode: cp.Code } });
      }
      for (const name of c.RelatedIfcEntityNamesList ?? []) {
        const target = `ifc:${name}`;
        if (ids.has(target)) edges.push({ id: `if:${c.Code}:${name}`, source: id, target, kind: "IfcReference", label: "IFC", ref: { type: "ifc", owner: c.Code, name } });
      }
    } else if (id.startsWith("p:")) {
      const p = idx.properties.get(id.slice(2));
      if (!p) continue;
      (p.PropertyRelations ?? []).forEach((r, i) => {
        const target = idForUri(doc, r.RelatedPropertyUri, "prop");
        if (!ids.has(target)) return;
        const kind = (EDGE_KINDS as readonly string[]).includes(r.RelationType) ? (r.RelationType as EdgeKind) : "HasReference";
        edges.push({ id: `pr:${p.Code}:${i}`, source: id, target, kind, label: r.RelationType, ref: { type: "propertyRelation", owner: p.Code, index: i } });
      });
    }
  }
  return edges;
}

export interface Neighbours {
  parent: string[];
  children: string[];
  relations: string[];
  properties: string[];
  classes: string[];
  ifc: string[];
}

/** Everything directly connected to a node (both directions), grouped. */
export function neighbours(doc: Doc, idx: Indexes, id: string): Neighbours {
  const d = doc.dictionary;
  const out: Neighbours = { parent: [], children: [], relations: [], properties: [], classes: [], ifc: [] };
  const add = (list: string[], v: string) => !list.includes(v) && v !== id && list.push(v);
  if (id.startsWith("c:")) {
    const code = id.slice(2);
    const c = idx.classes.get(code);
    if (!c) return out;
    if (c.ParentClassCode && idx.classes.has(c.ParentClassCode)) add(out.parent, classId(c.ParentClassCode));
    for (const k of idx.children.get(code) ?? []) add(out.children, classId(k.Code));
    for (const r of c.ClassRelations ?? []) add(out.relations, idForUri(doc, r.RelatedClassUri, "class"));
    for (const cp of c.ClassProperties ?? []) {
      const p = resolveProperty(idx, d, cp);
      if (p) add(out.properties, propId(p.Code));
      else if (cp.PropertyUri) add(out.properties, `xp:${cp.PropertyUri}`);
    }
    for (const n of c.RelatedIfcEntityNamesList ?? []) add(out.ifc, `ifc:${n}`);
    // reverse relations
    for (const other of d.Classes ?? []) {
      if (other.Code === code) continue;
      if ((other.ClassRelations ?? []).some((r) => internalCode(d, r.RelatedClassUri, "class") === code)) add(out.relations, classId(other.Code));
    }
  } else if (id.startsWith("p:")) {
    const code = id.slice(2);
    const p = idx.properties.get(code);
    if (!p) return out;
    for (const c of d.Classes ?? []) {
      if ((c.ClassProperties ?? []).some((cp) => cp.PropertyCode === code || internalCode(d, cp.PropertyUri, "prop") === code)) add(out.classes, classId(c.Code));
    }
    for (const r of p.PropertyRelations ?? []) add(out.relations, idForUri(doc, r.RelatedPropertyUri, "prop"));
    for (const other of d.Properties ?? []) {
      if (other.Code !== code && (other.PropertyRelations ?? []).some((r) => internalCode(d, r.RelatedPropertyUri, "prop") === code)) add(out.relations, propId(other.Code));
    }
  } else if (id.startsWith("xc:")) {
    const uri = id.slice(3).toLowerCase();
    for (const c of d.Classes ?? []) if ((c.ClassRelations ?? []).some((r) => r.RelatedClassUri.toLowerCase() === uri)) add(out.classes, classId(c.Code));
  } else if (id.startsWith("xp:")) {
    const uri = id.slice(3).toLowerCase();
    for (const c of d.Classes ?? []) if ((c.ClassProperties ?? []).some((cp) => cp.PropertyUri?.toLowerCase() === uri)) add(out.classes, classId(c.Code));
    for (const p of d.Properties ?? []) if ((p.PropertyRelations ?? []).some((r) => r.RelatedPropertyUri.toLowerCase() === uri)) add(out.relations, propId(p.Code));
  } else if (id.startsWith("ifc:")) {
    const name = id.slice(4);
    for (const c of d.Classes ?? []) if ((c.RelatedIfcEntityNamesList ?? []).includes(name)) add(out.classes, classId(c.Code));
  }
  return out;
}

/** Resolve free text (code, name, URI, IFC entity) to a node id. */
export function resolveInput(doc: Doc, idx: Indexes, text: string): string | null {
  const t = text.trim();
  if (!t) return null;
  if (t.startsWith("c:") || t.startsWith("p:")) return describeNode(doc, idx, t) ? t : null;
  if (isUri(t)) {
    const lower = t.toLowerCase();
    if (lower.includes("/prop/") || lower.includes("/property/")) return idForUri(doc, t, "prop");
    if (lower.includes("/uri/buildingsmart/ifc/") && lower.includes("/class/")) return `ifc:${lastSegment(t)}`;
    return idForUri(doc, t, "class");
  }
  if (idx.classes.has(t)) return classId(t);
  if (idx.properties.has(t)) return propId(t);
  const byName = (doc.dictionary.Classes ?? []).find((c) => c.Name.toLowerCase() === t.toLowerCase());
  if (byName) return classId(byName.Code);
  const propByName = (doc.dictionary.Properties ?? []).find((p) => p.Name.toLowerCase() === t.toLowerCase());
  if (propByName) return propId(propByName.Code);
  if (/^Ifc[A-Za-z0-9_]+$/.test(t)) return `ifc:${t}`;
  return null;
}

export { externalLabels };
