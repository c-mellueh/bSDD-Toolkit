import { ActionIcon, Group, Tooltip } from "@mantine/core";
import { useReadOnly } from "../state/readonly";
import { IconCheck, IconClipboard, IconCopy, IconEdit, IconLink, IconListSearch, IconPlus, IconRefresh, IconTrash } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { setGraphDrag } from "../graph/dnd";
import { classId, idForUri, propId } from "../graph/model";
import { copyClassProperties, readClip } from "../clipboard";
import { GOP, cpName, effectiveValues, linkedGop, resolveProperty } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { openUi } from "../state/ui";
import type { ClassProperty } from "../types";
import { divider, useContextMenu, type MenuItem } from "./ContextMenu";
import { askConfirm } from "./dialogs";
import { useListSelection } from "./useListSelection";
import { useColumnWidths } from "./useColumnWidths";

type SortKey = "name" | "code" | "pset" | "type" | "unit" | "values" | "required";

export function ClassPropertyTable({ classCode, pset, title }: { classCode: string | null; pset: string | null; title?: string }) {
  const { t } = useTranslation();
  const ro = useReadOnly();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const setActiveCp = useProject((s) => s.setActiveClassProperty);
  const openMenu = useContextMenu((s) => s.open);
  const cols = useColumnWidths("class-properties");
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 } | null>(null);
  const cls = classCode ? idx.classes.get(classCode) : undefined;
  const d = doc?.dictionary;

  const rows = useMemo(() => {
    if (!cls || !d) return [];
    const list = (cls.ClassProperties ?? []).filter((cp) => pset === null || (cp.PropertySet ?? "") === pset);
    const mapped = list.map((cp) => {
      const prop = resolveProperty(idx, d, cp);
      const { values, inherited } = effectiveValues(idx, d, cp);
      return {
        cp,
        name: cpName(idx, d, cp),
        type: prop?.DataType ?? "",
        unit: cp.Unit ?? "",
        values: values.map((v) => v.Value).join("; "),
        inherited: inherited && values.length > 0,
        linked: !!(cp.PropertySet && cls.ClassType !== GOP && linkedGop(idx, d, cls, cp.PropertySet)),
      };
    });
    if (sort) {
      const key = (r: (typeof mapped)[number]) =>
        ({ name: r.name, code: r.cp.Code, pset: r.cp.PropertySet ?? "", type: r.type, unit: r.unit, values: r.values, required: r.cp.IsRequired ? "1" : "0" })[sort.key];
      mapped.sort((a, b) => key(a).localeCompare(key(b)) * sort.dir);
    }
    return mapped;
  }, [cls, d, idx, pset, sort]);

  const keys = rows.map((r) => r.cp.Code);
  const sel = useListSelection(keys);

  if (!doc || !d) return null;

  const selected = (): ClassProperty[] => rows.filter((r) => sel.selected.includes(r.cp.Code)).map((r) => r.cp);
  const newCp = () => cls && openUi({ cpEditor: { classCode: cls.Code, pset: pset ?? undefined } });
  const edit = (code: string) => cls && openUi({ cpEditor: { classCode: cls.Code, code } });
  const remove = async () => {
    const cps = selected();
    if (!cls || !cps.length) return;
    const ok = await askConfirm(t("Delete class properties"), t("Delete {{n}} class properties?", { n: cps.length }), t("Delete"), true);
    if (ok) await attempt(() => op("cp.delete", { class_code: cls.Code, codes: cps.map((c) => c.Code) }));
  };
  const copy = () => {
    const cps = selected();
    if (!cps.length) return;
    copyClassProperties(idx, doc, cps);
    notifyOk(t("{{n}} class properties copied", { n: cps.length }));
  };
  const paste = async () => {
    const clip = readClip("bsdd-class-properties");
    if (!clip || !cls) return;
    await attempt(() => op("cp.paste", { class_code: cls.Code, payload: clip, pset }));
  };
  const addExisting = () =>
    cls &&
    openUi({
      search: {
        kind: "property",
        onPick: (code) => void attempt(() => op("cp.add_properties", { class_code: cls.Code, property_codes: [code], pset: pset ?? undefined })),
      },
    });
  const syncValues = async () => {
    const cps = selected();
    if (!cls || !cps.length) return;
    const n = await attempt(() => op<number>("gop.sync_allowed_values", { class_code: cls.Code, codes: cps.map((c) => c.Code) }));
    if (n !== undefined) notifyOk(t("Allowed values synchronised ({{n}})", { n }));
  };

  const menu = (): MenuItem[] => {
    const items: MenuItem[] = [
      { label: t("New"), icon: <IconPlus size={14} />, shortcut: "Ctrl+N", onClick: newCp },
      { label: t("Add existing property…"), icon: <IconListSearch size={14} />, onClick: addExisting },
      { label: t("Edit"), icon: <IconEdit size={14} />, onClick: () => sel.selected[0] && edit(sel.selected[0]), disabled: !sel.selected.length },
      divider,
      { label: t("Copy"), icon: <IconCopy size={14} />, shortcut: "Ctrl+C", onClick: copy, disabled: !sel.selected.length },
      { label: t("Paste"), icon: <IconClipboard size={14} />, shortcut: "Ctrl+V", onClick: paste, disabled: !readClip("bsdd-class-properties") },
    ];
    if (cls?.ClassType === GOP) items.push(divider, { label: t("Sync allowed values"), icon: <IconRefresh size={14} />, onClick: syncValues, disabled: !sel.selected.length });
    items.push(divider, { label: t("Delete"), icon: <IconTrash size={14} />, color: "red", shortcut: "Del", onClick: remove, disabled: !sel.selected.length });
    return items;
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if ((e.target as HTMLElement).tagName === "INPUT") return;
    const ctrl = e.ctrlKey || e.metaKey;
    const k = e.key.toLowerCase();
    if (ctrl && k === "c") { e.preventDefault(); copy(); }
    else if (ctrl && k === "v") { e.preventDefault(); void paste(); }
    else if (ctrl && k === "n") { e.preventDefault(); newCp(); }
    else if (ctrl && k === "a") { e.preventDefault(); sel.setSelected(keys); }
    else if (e.key === "Delete") { e.preventDefault(); void remove(); }
    else if (e.key === "Enter" && sel.selected[0]) { e.preventDefault(); edit(sel.selected[0]); }
  };

  const header = (key: SortKey, label: string, width?: number | string) => (
    <th data-col={key !== "values" ? key : undefined} style={{ width: cols.width(key, width) }} onClick={() => setSort((s) => (s?.key === key ? (s.dir === 1 ? { key, dir: -1 } : null) : { key, dir: 1 }))}>
      {label}
      {sort?.key === key ? (sort.dir === 1 ? " ▲" : " ▼") : ""}
      {key !== "values" && cols.handle(key)}
    </th>
  );

  return (
    <div className="pane">
      <div className="pane-header">
        <span className="pane-title" style={{ flex: 1 }}>
          {title ?? t("Class properties")}
          {cls ? ` · ${cls.Name}${pset !== null ? ` · ${pset || t("(no property set)")}` : ""}` : ""}
        </span>
        {cls && !ro && (
          <Group gap={2}>
            <Tooltip label={t("Add existing property…")}><ActionIcon variant="subtle" size="sm" onClick={addExisting}><IconListSearch size={16} /></ActionIcon></Tooltip>
            <Tooltip label={t("New class property") + " (Ctrl+N)"}><ActionIcon variant="light" size="sm" onClick={newCp}><IconPlus size={16} /></ActionIcon></Tooltip>
          </Group>
        )}
      </div>
      <div className="pane-body" tabIndex={-1} onKeyDown={onKeyDown}
        onContextMenu={(e) => { if (cls && (e.target as HTMLElement).closest("tr") === null) openMenu(e, menu()); }}>
        {!cls && <div className="empty-hint">{t("Select a class")}</div>}
        {cls && (
          <table className="grid-table" style={{ tableLayout: "fixed", minWidth: cols.total ? cols.total + 140 : undefined }}>
            <thead>
              <tr>
                {header("name", t("Name"), "24%")}
                {header("code", t("Code"), "18%")}
                {pset === null && header("pset", t("Property set"), "14%")}
                {header("type", t("Datatype"), 80)}
                {header("unit", t("Unit"), 60)}
                {header("values", t("Values"))}
                {header("required", t("Required"), 64)}
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr
                  key={r.cp.Code}
                  className={sel.selected.includes(r.cp.Code) ? "selected" : ""}
                  onClick={(e) => { sel.click(r.cp.Code, e); setActiveCp(r.cp.Code); }}
                  onDoubleClick={() => edit(r.cp.Code)}
                  draggable
                  onDragStart={(e) => {
                    const chosen = sel.selected.includes(r.cp.Code) ? rows.filter((x) => sel.selected.includes(x.cp.Code)) : [r];
                    const ids = chosen.map((x) => (x.cp.PropertyCode ? propId(x.cp.PropertyCode) : x.cp.PropertyUri ? idForUri(doc!, x.cp.PropertyUri, "prop") : null));
                    setGraphDrag(e, [...(cls ? [classId(cls.Code)] : []), ...ids.filter((x): x is string => !!x)]);
                  }}
                  onContextMenu={(e) => { sel.ensure(r.cp.Code); openMenu(e, menu()); }}
                >
                  <td title={r.name}>
                    {r.linked && <IconLink size={12} style={{ marginRight: 4, opacity: 0.6 }} />}
                    {r.name}
                  </td>
                  <td title={r.cp.Code}>{r.cp.Code}</td>
                  {pset === null && <td title={r.cp.PropertySet ?? ""}>{r.cp.PropertySet ?? ""}</td>}
                  <td title={r.type}>{r.type}</td>
                  <td title={r.unit}>{r.unit}</td>
                  <td title={r.values} style={r.inherited ? { opacity: 0.55, fontStyle: "italic" } : undefined}>{r.values}</td>
                  <td>{r.cp.IsRequired ? <IconCheck size={14} /> : null}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {cls && rows.length === 0 && <div className="empty-hint">{t("No class properties")}</div>}
      </div>
    </div>
  );
}
