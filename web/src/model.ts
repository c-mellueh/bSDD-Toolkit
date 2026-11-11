import type { BsddClass, BsddProperty, ClassProperty, Dictionary, Doc } from "./types";

export const GOP = "GroupOfProperties";
export const MATERIAL = "Material";

/** Which tree / page a class is shown in: classes, groups of properties or materials. */
export type ClassMode = "main" | "gop" | "material";
export const classMode = (c?: { ClassType?: string | null } | null): ClassMode =>
  c?.ClassType === GOP ? "gop" : c?.ClassType === MATERIAL ? "material" : "main";
/** ClassType of new classes created in a tree of the given mode. */
export const MODE_CLASS_TYPE: Record<ClassMode, string> = { main: "Class", gop: GOP, material: MATERIAL };
export const CLASS_TYPES = ["Class", "GroupOfProperties", "AlternativeUse", "Material", "ReferenceDocument", "ComposedProperty"];
export const CLASS_STATUSES = ["Preview", "Active", "Inactive"];
export const DATA_TYPES = ["Boolean", "Character", "Integer", "Real", "String", "Time"];
export const PROPERTY_VALUE_KINDS = ["Single", "Range", "List", "Complex", "ComplexList"];
export const CLASS_RELATION_TYPES = ["HasMaterial", "HasReference", "IsEqualTo", "IsSimilarTo", "IsParentOf", "IsChildOf", "HasPart", "IsPartOf"];
export const PROPERTY_RELATION_TYPES = ["HasReference", "IsEqualTo", "IsSimilarTo"];
export const BASE_URI = "https://identifier.buildingsmart.org";

export interface Indexes {
  classes: Map<string, BsddClass>;
  children: Map<string | null, BsddClass[]>;
  properties: Map<string, BsddProperty>;
}

export function buildIndexes(doc: Doc | null): Indexes {
  const classes = new Map<string, BsddClass>();
  const children = new Map<string | null, BsddClass[]>();
  const properties = new Map<string, BsddProperty>();
  if (!doc) return { classes, children, properties };
  for (const c of doc.dictionary.Classes ?? []) classes.set(c.Code, c);
  for (const c of doc.dictionary.Classes ?? []) {
    const parent = c.ParentClassCode && classes.has(c.ParentClassCode) ? c.ParentClassCode : null;
    if (!children.has(parent)) children.set(parent, []);
    children.get(parent)!.push(c);
  }
  for (const p of doc.dictionary.Properties ?? []) properties.set(p.Code, p);
  return { classes, children, properties };
}

const GERMAN: Record<string, string> = { ä: "ae", ö: "oe", ü: "ue", Ä: "Ae", Ö: "Oe", Ü: "Ue", ß: "ss" };

/** Same rules as bsdd_json.utils.dictionary_utils.slugify (lowercase=False). */
export function slugify(text: string): string {
  let s = String(text ?? "");
  s = s.replace(/[äöüÄÖÜß]/g, (c) => GERMAN[c]);
  s = s.normalize("NFKD").replace(/[̀-ͯ]/g, "");
  s = s.replace(/[^A-Za-z0-9]+/g, "-");
  s = s.replace(/-+/g, "-").replace(/^-|-$/g, "");
  return s;
}

export function uniqueCode(base: string, existing: Iterable<string>): string {
  const set = new Set(existing);
  if (!set.has(base)) return base;
  let i = 2;
  while (set.has(`${base}-${i}`)) i++;
  return `${base}-${i}`;
}

function host(d: Dictionary) {
  if (d.UseOwnUri && d.DictionaryUri) {
    try {
      return new URL(d.DictionaryUri).origin;
    } catch {
      return d.DictionaryUri.replace(/\/$/, "");
    }
  }
  return BASE_URI;
}

export function classUri(d: Dictionary, code: string): string {
  return `${host(d)}/uri/${d.OrganizationCode}/${d.DictionaryCode}/${d.DictionaryVersion}/class/${code}`;
}

export function propertyUri(d: Dictionary, code: string): string {
  return `${host(d)}/uri/${d.OrganizationCode}/${d.DictionaryCode}/${d.DictionaryVersion}/prop/${code}`;
}

export function isUri(s: string | undefined | null): boolean {
  if (!s) return false;
  try {
    const u = new URL(s);
    return !!u.protocol && !!u.host;
  } catch {
    return false;
  }
}

/** Code of an internal class/property if the URI points into this dictionary (any version). */
export function internalCode(d: Dictionary, uri: string | undefined, kind: "class" | "prop"): string | null {
  if (!uri || !isUri(uri)) return null;
  const parts = new URL(uri).pathname.split("/").filter(Boolean);
  const i = parts.indexOf("uri");
  const after = i >= 0 ? parts.slice(i + 1) : parts;
  if (after.length < 5) return null;
  if (`${after[0]}/${after[1]}`.toLowerCase() !== `${d.OrganizationCode}/${d.DictionaryCode}`.toLowerCase()) return null;
  const type = after[3];
  if (kind === "class" && type !== "class") return null;
  if (kind === "prop" && type !== "prop" && type !== "property") return null;
  return after[4];
}

export function codeFromUri(uri: string): string {
  const parts = uri.split("/").filter(Boolean);
  return parts[parts.length - 1] ?? uri;
}

export function psetsOfClass(doc: Doc, cls: BsddClass | undefined): string[] {
  if (!cls) return [];
  const names: string[] = [];
  for (const cp of cls.ClassProperties ?? []) {
    const n = cp.PropertySet ?? "";
    if (!names.includes(n)) names.push(n);
  }
  for (const n of doc.extras.temporary_psets?.[cls.Code] ?? []) if (!names.includes(n)) names.push(n);
  return names;
}

export function resolveProperty(idx: Indexes, d: Dictionary, cp: ClassProperty): BsddProperty | undefined {
  if (cp.PropertyCode) return idx.properties.get(cp.PropertyCode);
  if (cp.PropertyUri) {
    const code = internalCode(d, cp.PropertyUri, "prop");
    if (code) return idx.properties.get(code);
  }
  return undefined;
}

/** Properties of this dictionary used by the groups of properties among ``codes`` (classes about to
 * be deleted). ``names``: would be deleted; ``kept``: also used in another property set, so they stay;
 * ``otherClasses``: remaining classes that use the ones to delete (in this property set). */
export function gopPropertyUsage(idx: Indexes, d: Dictionary, codes: string[]): { names: string[]; kept: string[]; otherClasses: number } {
  const deleting = new Set(codes);
  const props = new Map<string, string>();
  const psetNames = new Set<string>();
  for (const code of codes) {
    const c = idx.classes.get(code);
    if (c?.ClassType !== GOP) continue;
    psetNames.add(c.Name);
    for (const cp of c.ClassProperties ?? []) {
      const p = resolveProperty(idx, d, cp);
      if (p) props.set(p.Code, p.Name || p.Code);
    }
  }
  const kept = new Map<string, string>();
  if (props.size) {
    for (const c of d.Classes ?? []) {
      if (deleting.has(c.Code)) continue;
      for (const cp of c.ClassProperties ?? []) {
        if (psetNames.has(cp.PropertySet ?? "")) continue;
        const code = resolveProperty(idx, d, cp)?.Code;
        if (code && props.has(code)) {
          kept.set(code, props.get(code)!);
          props.delete(code);
        }
      }
    }
  }
  let otherClasses = 0;
  if (props.size) {
    for (const c of d.Classes ?? []) {
      if (deleting.has(c.Code)) continue;
      if ((c.ClassProperties ?? []).some((cp) => props.has(resolveProperty(idx, d, cp)?.Code ?? ""))) otherClasses++;
    }
  }
  const sorted = (m: Map<string, string>) => [...m.values()].sort((a, b) => a.localeCompare(b));
  return { names: sorted(props), kept: sorted(kept), otherClasses };
}

export function cpName(idx: Indexes, d: Dictionary, cp: ClassProperty): string {
  const p = resolveProperty(idx, d, cp);
  if (p) return p.Name;
  if (cp.PropertyUri) return codeFromUri(cp.PropertyUri);
  return cp.Code;
}

/** Allowed values of a class property, falling back to the property definition. */
export function effectiveValues(idx: Indexes, d: Dictionary, cp: ClassProperty) {
  if (cp.AllowedValues?.length) return { values: cp.AllowedValues, inherited: false };
  const p = resolveProperty(idx, d, cp);
  return { values: p?.AllowedValues ?? [], inherited: true };
}

/** Is a pset of `cls` linked to an internal GroupOfProperties via HasReference? */
export function linkedGop(idx: Indexes, d: Dictionary, cls: BsddClass, pset: string): BsddClass | undefined {
  for (const cr of cls.ClassRelations ?? []) {
    if (cr.RelationType !== "HasReference") continue;
    const code = internalCode(d, cr.RelatedClassUri, "class");
    const target = code ? idx.classes.get(code) : undefined;
    if (target && target.ClassType === GOP && target.Name === pset) return target;
  }
  return undefined;
}

export function ancestors(idx: Indexes, code: string): string[] {
  const out: string[] = [];
  let cur = idx.classes.get(code)?.ParentClassCode;
  const seen = new Set<string>();
  while (cur && !seen.has(cur) && idx.classes.has(cur)) {
    seen.add(cur);
    out.push(cur);
    cur = idx.classes.get(cur)?.ParentClassCode;
  }
  return out;
}

export function descendants(idx: Indexes, code: string): string[] {
  const out: string[] = [];
  const seen = new Set<string>([code]);
  const stack = [code];
  while (stack.length) {
    const cur = stack.pop()!;
    for (const child of idx.children.get(cur) ?? []) {
      if (!seen.has(child.Code)) {
        seen.add(child.Code);
        out.push(child.Code);
        stack.push(child.Code);
      }
    }
  }
  return out;
}

/** Remove empty strings / empty arrays / undefined so the backend gets clean data. */
export function clean<T extends Record<string, unknown>>(data: T): T {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(data)) {
    if (v === "" || v === undefined) out[k] = null;
    else if (Array.isArray(v) && v.length === 0 && k !== "AllowedValues" && k !== "ClassRelations" && k !== "PropertyRelations") out[k] = null;
    else out[k] = v;
  }
  return out as T;
}

// --------------------------------------------------------------- strict inheritance

/** Identity of a class property for inheritance: property set + referenced property. */
export function cpKey(d: Dictionary, cp: ClassProperty): string {
  const code = cp.PropertyCode || internalCode(d, cp.PropertyUri, "prop");
  const ref = code ? `code:${code}` : `uri:${(cp.PropertyUri ?? "").trim().replace(/\/+$/, "").toLowerCase()}`;
  return `${cp.PropertySet ?? ""}\u0000${ref}`;
}

/** The parent class that passes on its class properties (strict inheritance only). */
export function inheritanceParent(idx: Indexes, doc: Doc, cls: BsddClass): BsddClass | undefined {
  if (!doc.extras?.strict_inheritance || cls.ClassType === GOP || !cls.ParentClassCode) return undefined;
  const parent = idx.classes.get(cls.ParentClassCode);
  return parent && parent.ClassType !== GOP ? parent : undefined;
}

/** Keys of the class properties ``cls`` inherits (empty without strict inheritance). */
export function inheritedKeys(idx: Indexes, doc: Doc, cls: BsddClass): Set<string> {
  const parent = inheritanceParent(idx, doc, cls);
  return new Set((parent?.ClassProperties ?? []).map((cp) => cpKey(doc.dictionary, cp)));
}

/** How many class properties switching strict inheritance on would add. */
export function missingInherited(idx: Indexes, doc: Doc): number {
  const d = doc.dictionary;
  const have = new Map<string, Set<string>>();
  for (const c of d.Classes ?? []) have.set(c.Code, new Set((c.ClassProperties ?? []).map((cp) => cpKey(d, cp))));
  const effective = (code: string) => have.get(code)!;
  let added = 0;
  const visit = (parent: BsddClass, seen: Set<string>) => {
    for (const child of idx.children.get(parent.Code) ?? []) {
      if (child.ClassType === GOP || parent.ClassType === GOP || seen.has(child.Code)) continue;
      seen.add(child.Code);
      const mine = effective(child.Code);
      for (const k of effective(parent.Code)) if (!mine.has(k)) { mine.add(k); added++; }
      visit(child, seen);
    }
  };
  const seen = new Set<string>();
  for (const root of idx.children.get(null) ?? []) visit(root, seen);
  return added;
}
