/* eslint-disable @typescript-eslint/no-explicit-any */
import type { BsddClass, BsddProperty, ClassProperty, Doc } from "./types";
import type { Indexes } from "./model";
import { descendants, resolveProperty } from "./model";

/**
 * In-app clipboard: stored in localStorage (works across tabs and without HTTPS) and
 * additionally copied to the system clipboard when available.
 */
const KEY = "bsdd-clipboard";

export type ClipKind = "bsdd-classes" | "bsdd-class-properties" | "bsdd-psets" | "bsdd-properties";

export function writeClip(kind: ClipKind, payload: Record<string, any>) {
  const data = JSON.stringify({ kind, ...payload });
  try {
    localStorage.setItem(KEY, data);
  } catch {
    /* ignore */
  }
  try {
    void navigator.clipboard?.writeText(data);
  } catch {
    /* insecure context */
  }
}

export function readClip(kind: ClipKind): Record<string, any> | null {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const data = JSON.parse(raw);
    return data.kind === kind ? data : null;
  } catch {
    return null;
  }
}

function referencedProperties(idx: Indexes, doc: Doc, cps: ClassProperty[]): BsddProperty[] {
  const out = new Map<string, BsddProperty>();
  for (const cp of cps) {
    const p = resolveProperty(idx, doc.dictionary, cp);
    if (p && cp.PropertyCode) out.set(p.Code, p);
  }
  return [...out.values()];
}

export function copyClasses(idx: Indexes, doc: Doc, codes: string[], withChildren: boolean) {
  const set = new Set<string>();
  for (const code of codes) {
    set.add(code);
    if (withChildren) for (const d of descendants(idx, code)) set.add(d);
  }
  const classes: BsddClass[] = (doc.dictionary.Classes ?? []).filter((c) => set.has(c.Code));
  const cps = classes.flatMap((c) => c.ClassProperties ?? []);
  writeClip("bsdd-classes", { classes, properties: referencedProperties(idx, doc, cps) });
  return classes.length;
}

export function copyClassProperties(idx: Indexes, doc: Doc, cps: ClassProperty[]) {
  writeClip("bsdd-class-properties", { class_properties: cps, properties: referencedProperties(idx, doc, cps) });
}

export function copyPsets(idx: Indexes, doc: Doc, cls: BsddClass, names: string[]) {
  const items = names.map((name) => ({ name, properties: (cls.ClassProperties ?? []).filter((cp) => (cp.PropertySet ?? "") === name) }));
  const cps = items.flatMap((i) => i.properties);
  writeClip("bsdd-psets", { items, properties: referencedProperties(idx, doc, cps) });
}

export function copyProperties(props: BsddProperty[]) {
  writeClip("bsdd-properties", { properties: props });
}

/** Parse pasted text for allowed values: CSV with ';' columns or one value per separator. */
export function parseValuesText(text: string, separator: string): string[][] {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.trim() !== "");
  if (lines.some((l) => l.includes(";")) || lines.some((l) => l.includes("\t"))) {
    return lines.map((l) => l.split(/[;\t]/).map((s) => s.trim()));
  }
  const sep = separator === "\\n" || separator === "" ? "\n" : separator;
  return text.split(sep).map((s) => s.trim()).filter(Boolean).map((v) => [v]);
}
