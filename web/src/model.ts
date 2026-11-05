import type { BsddClass, BsddProperty, ClassProperty, Dictionary, Doc } from "./types";

export const GOP = "GroupOfProperties";
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
  const stack = [code];
  while (stack.length) {
    const cur = stack.pop()!;
    for (const child of idx.children.get(cur) ?? []) {
      if (!out.includes(child.Code)) {
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
