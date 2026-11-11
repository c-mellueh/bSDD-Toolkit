/** Side panel listing the dictionary's classes / groups of properties / materials / properties; items can be dragged into the graph. */
import { SegmentedControl, Text, TextInput } from "@mantine/core";
import { IconChevronDown, IconChevronRight, IconSearch } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { classMode, descendants, type ClassMode, type Indexes } from "../model";
import type { BsddClass, Doc } from "../types";
import { setGraphDrag } from "./dnd";
import { NODE_STYLE, classId, propId } from "./model";

type Tab = "classes" | "gop" | "material" | "props";
const TAB_MODE: Record<Exclude<Tab, "props">, ClassMode> = { classes: "main", gop: "gop", material: "material" };
const TAB_KIND = { classes: "Class", gop: "GroupOfProperties", material: "Material" } as const;
interface Row {
  id: string;
  label: string;
  sub: string;
  depth: number;
  color: string;
  hasKids?: boolean;
  open?: boolean;
}

const LIMIT = 600;

function matches(q: string, ...texts: (string | undefined | null)[]) {
  return texts.some((t) => t && t.toLowerCase().includes(q));
}

export function GraphLibrary({ doc, idx, inScene, onAdd }: { doc: Doc; idx: Indexes; inScene: Set<string>; onAdd: (ids: string[]) => void }) {
  const { t } = useTranslation();
  const [tab, setTab] = useState<Tab>("classes");
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<string[]>([]);
  const [anchor, setAnchor] = useState<string | null>(null);

  const rows = useMemo<Row[]>(() => {
    const q = query.trim().toLowerCase();
    const out: Row[] = [];
    if (tab === "props") {
      const props = [...(doc.dictionary.Properties ?? [])].sort((a, b) => (a.Name ?? "").localeCompare(b.Name ?? "", undefined, { numeric: true }));
      for (const p of props) if (!q || matches(q, p.Name, p.Code)) out.push({ id: propId(p.Code), label: p.Name || p.Code, sub: p.Code, depth: 0, color: NODE_STYLE.Property.color });
      return out;
    }
    const include = (c: BsddClass) => classMode(c) === TAB_MODE[tab];
    const color = NODE_STYLE[TAB_KIND[tab]].color;
    if (q) {
      const list = (doc.dictionary.Classes ?? []).filter((c) => include(c) && matches(q, c.Name, c.Code));
      list.sort((a, b) => (a.Name ?? "").localeCompare(b.Name ?? "", undefined, { numeric: true }));
      for (const c of list) out.push({ id: classId(c.Code), label: c.Name || c.Code, sub: c.Code, depth: 0, color });
      return out;
    }
    // hierarchy
    const roots = (doc.dictionary.Classes ?? []).filter((c) => include(c) && (!c.ParentClassCode || !idx.classes.has(c.ParentClassCode) || !include(idx.classes.get(c.ParentClassCode)!)));
    const walk = (c: BsddClass, depth: number) => {
      if (out.length > LIMIT * 4) return;
      const kids = (idx.children.get(c.Code) ?? []).filter(include);
      const isOpen = open.has(c.Code);
      out.push({ id: classId(c.Code), label: c.Name || c.Code, sub: c.Code, depth, color, hasKids: kids.length > 0, open: isOpen });
      if (isOpen) for (const k of kids) walk(k, depth + 1);
    };
    for (const r of roots) walk(r, 0);
    return out;
  }, [doc, idx, tab, query, open]);

  const shown = rows.slice(0, LIMIT);

  // dragging a collapsed class also brings all its (sub)children, an expanded one only itself
  const withCollapsedChildren = (ids: string[]) => {
    const byId = new Map(rows.map((r) => [r.id, r]));
    const out = new Set<string>();
    for (const id of ids) {
      out.add(id);
      const r = byId.get(id);
      if (r?.hasKids && !r.open) descendants(idx, id.slice(2)).forEach((c) => out.add(classId(c)));
    }
    return [...out];
  };

  const click = (id: string, e: React.MouseEvent) => {
    if (e.shiftKey && anchor) {
      const ids = shown.map((r) => r.id);
      const [a, b] = [ids.indexOf(anchor), ids.indexOf(id)].sort((x, y) => x - y);
      if (a >= 0) {
        setSelected(ids.slice(a, b + 1));
        return;
      }
    }
    if (e.ctrlKey || e.metaKey) setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
    else setSelected([id]);
    setAnchor(id);
  };

  const toggle = (code: string) =>
    setOpen((s) => {
      const n = new Set(s);
      if (n.has(code)) n.delete(code);
      else n.add(code);
      return n;
    });

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", minHeight: 0 }}>
      <div style={{ padding: 6, display: "flex", flexDirection: "column", gap: 6, borderBottom: "1px solid var(--mantine-color-default-border)" }}>
        <SegmentedControl
          size="xs"
          fullWidth
          value={tab}
          onChange={(v) => { setTab(v as Tab); setSelected([]); }}
          data={[
            { value: "classes", label: t("Classes") },
            { value: "gop", label: t("Groups") },
            { value: "material", label: t("Materials") },
            { value: "props", label: t("Properties") },
          ]}
        />
        <TextInput size="xs" leftSection={<IconSearch size={14} />} placeholder={t("Filter…")} value={query} onChange={(e) => setQuery(e.currentTarget.value)} />
        <Text size="xs" c="dimmed">{t("Drag items into the graph (or double-click). Ctrl/Shift selects several.")}</Text>
      </div>
      <div style={{ flex: 1, overflow: "auto", minHeight: 0 }}>
        {shown.map((r) => {
          const code = r.id.slice(2);
          const isSel = selected.includes(r.id);
          const present = inScene.has(r.id);
          return (
            <div
              key={r.id}
              className={`row${isSel ? " selected" : ""}`}
              draggable
              onDragStart={(e) => setGraphDrag(e, withCollapsedChildren(isSel ? selected : [r.id]))}
              onClick={(e) => click(r.id, e)}
              onDoubleClick={() => onAdd(isSel ? selected : [r.id])}
              title={`${r.label} (${r.sub})${present ? " – " + t("in the graph") : ""}`}
              style={{ paddingLeft: 4 + r.depth * 12, cursor: "grab", height: 24, display: "flex", alignItems: "center", gap: 4 }}
            >
              <span style={{ width: 14, flex: "none", display: "inline-flex" }} onClick={(e) => { if (r.hasKids) { e.stopPropagation(); toggle(code); } }}>
                {r.hasKids ? r.open ? <IconChevronDown size={12} /> : <IconChevronRight size={12} /> : null}
              </span>
              <span style={{ width: 8, height: 8, borderRadius: 4, flex: "none", background: present ? r.color : "transparent", border: `1.5px solid ${r.color}` }} />
              <span style={{ flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 13 }}>{r.label}</span>
              <span style={{ maxWidth: "40%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: 11, opacity: 0.6 }}>{r.sub}</span>
            </div>
          );
        })}
        {rows.length > LIMIT && <Text size="xs" c="dimmed" p={6}>{t("{{n}} more – refine the filter", { n: rows.length - LIMIT })}</Text>}
        {rows.length === 0 && <Text size="xs" c="dimmed" p={6}>{t("Nothing found")}</Text>}
      </div>
    </div>
  );
}
