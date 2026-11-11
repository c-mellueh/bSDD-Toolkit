import { ActionIcon, Autocomplete, Group, Tooltip } from "@mantine/core";
import { useReadOnly } from "../state/readonly";
import { IconClipboard, IconCopy, IconEdit, IconLink, IconPlus, IconTrash } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { copyPsets, readClip } from "../clipboard";
import { GOP, linkedGop, psetsOfClass } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { divider, useContextMenu } from "./ContextMenu";
import { askConfirm, askText } from "./dialogs";
import { useListSelection } from "./useListSelection";
import { useSettings } from "../state/settings";

export function PsetList() {
  const { t } = useTranslation();
  const ro = useReadOnly();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const activeClass = useProject((s) => s.activeClass);
  const activePset = useProject((s) => s.activePset);
  const setActivePset = useProject((s) => s.setActivePset);
  const openMenu = useContextMenu((s) => s.open);
  const [newName, setNewName] = useState("");
  const cls = activeClass ? idx.classes.get(activeClass) : undefined;
  const psets = useMemo(() => (doc && cls ? psetsOfClass(doc, cls) : []), [doc, cls]);
  const sel = useListSelection(psets);

  const gopNames = useMemo(
    () => (doc?.dictionary.Classes ?? []).filter((c) => c.ClassType === GOP && c.Code !== cls?.Code && !psets.includes(c.Name)).map((c) => c.Name),
    [doc, cls, psets],
  );

  if (!doc) return null;

  const counts = new Map<string, number>();
  for (const cp of cls?.ClassProperties ?? []) counts.set(cp.PropertySet ?? "", (counts.get(cp.PropertySet ?? "") ?? 0) + 1);

  const create = async () => {
    if (!cls) return;
    const name = newName.trim() || t("New PropertySet");
    const created = await attempt(() => op<string>("pset.create", { class_code: cls.Code, name, auto_gop: useSettings.getState().autoCreateGop, gop_prefix: useSettings.getState().gopPrefix }));
    if (created) {
      setActivePset(created);
      setNewName("");
    }
  };

  const rename = async (name: string) => {
    if (!cls) return;
    const value = await askText(t("Rename property set"), t("New name"), name);
    if (!value || value === name) return;
    const created = await attempt(() => op<string>("pset.rename", { class_code: cls.Code, old: name, new: value }));
    if (created) setActivePset(created);
  };

  const remove = async () => {
    if (!cls) return;
    const names = sel.selected.length ? sel.selected : activePset !== null ? [activePset] : [];
    if (!names.length) return;
    const ok = await askConfirm(t("Delete property sets"), t("Delete {{names}} and all contained class properties?", { names: names.join(", ") }), t("Delete"), true);
    if (!ok) return;
    await attempt(() => op("pset.delete", { class_code: cls.Code, names }));
    setActivePset(null);
  };

  const copy = () => {
    if (!cls) return;
    const names = sel.selected.length ? sel.selected : activePset !== null ? [activePset] : [];
    copyPsets(idx, doc, cls, names);
    notifyOk(t("Copied"));
  };

  const paste = async () => {
    const clip = readClip("bsdd-psets");
    if (!clip || !cls) return;
    await attempt(() => op("pset.paste", { class_code: cls.Code, payload: clip }));
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if ((e.target as HTMLElement).tagName === "INPUT") return;
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === "c") { e.preventDefault(); copy(); }
    else if (ctrl && e.key.toLowerCase() === "v") { e.preventDefault(); void paste(); }
    else if (e.key === "Delete") { e.preventDefault(); void remove(); }
    else if (e.key === "F2" && activePset !== null) { e.preventDefault(); void rename(activePset); }
  };

  return (
    <div className="pane">
      <div className="pane-header">
        <span className="pane-title" style={{ flex: 1 }}>{t("Property sets")}</span>
      </div>
      {cls && !ro && (
        <Group gap={4} p={6} wrap="nowrap" style={{ borderBottom: "1px solid var(--mantine-color-default-border)" }}>
          <Autocomplete
            placeholder={t("New PropertySet")}
            data={gopNames}
            value={newName}
            onChange={setNewName}
            style={{ flex: 1 }}
            onKeyDown={(e) => e.key === "Enter" && create()}
          />
          <Tooltip label={t("Add property set (names of Groups of Properties are linked)")}>
            <ActionIcon aria-label={t("Add property set (names of Groups of Properties are linked)")} variant="light" onClick={create}><IconPlus size={16} /></ActionIcon>
          </Tooltip>
        </Group>
      )}
      <div className="pane-body" tabIndex={-1} onKeyDown={onKeyDown}
        onContextMenu={(e) => { if (cls && e.target === e.currentTarget) openMenu(e, [{ label: t("Paste"), onClick: paste, disabled: !readClip("bsdd-psets") }]); }}>
        {!cls && <div className="empty-hint">{t("Select a class")}</div>}
        {cls && psets.length === 0 && <div className="empty-hint">{t("No property sets")}</div>}
        {cls &&
          psets.map((name) => {
            const linked = name && linkedGop(idx, doc.dictionary, cls, name);
            const isSel = sel.selected.includes(name) || activePset === name;
            return (
              <div
                key={name || "∅"}
                className={`row${isSel ? " selected" : ""}`}
                onClick={(e) => { sel.click(name, e); setActivePset(name); }}
                onDoubleClick={() => rename(name)}
                onContextMenu={(e) => {
                  sel.ensure(name);
                  setActivePset(name);
                  openMenu(e, [
                    { label: t("Rename"), icon: <IconEdit size={14} />, shortcut: "F2", onClick: () => rename(name) },
                    { label: t("Copy"), icon: <IconCopy size={14} />, shortcut: "Ctrl+C", onClick: copy },
                    { label: t("Paste"), icon: <IconClipboard size={14} />, shortcut: "Ctrl+V", onClick: paste, disabled: !readClip("bsdd-psets") },
                    divider,
                    { label: t("Delete"), icon: <IconTrash size={14} />, color: "red", shortcut: "Del", onClick: remove },
                  ]);
                }}
              >
                <span className="cell" style={{ flex: 1 }}>{name || <i>{t("(no property set)")}</i>}</span>
                {linked && <Tooltip label={t("Linked to Group of Properties")}><IconLink size={14} style={{ opacity: 0.7 }} /></Tooltip>}
                <span className="cell" style={{ opacity: 0.5, fontSize: 12 }}>{counts.get(name) ?? 0}</span>
              </div>
            );
          })}
      </div>
    </div>
  );
}
