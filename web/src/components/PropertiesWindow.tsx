import { ActionIcon, Group, Modal, TextInput, Tooltip } from "@mantine/core";
import { IconClipboard, IconCopy, IconEdit, IconPlus, IconSquarePlus, IconTrash } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { setGraphDrag } from "../graph/dnd";
import { classId, propId } from "../graph/model";
import { copyProperties, readClip } from "../clipboard";
import { internalCode } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { openUi, useUi } from "../state/ui";
import { divider, useContextMenu } from "./ContextMenu";
import { askConfirm } from "./dialogs";
import { useListSelection } from "./useListSelection";

export function PropertiesWindow() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.propertiesWindow);
  const close = () => useUi.getState().set({ propertiesWindow: false });
  const doc = useProject((s) => s.doc);
  const activeClass = useProject((s) => s.activeClass);
  const activePset = useProject((s) => s.activePset);
  const openMenu = useContextMenu((s) => s.open);
  const [filter, setFilter] = useState("");
  const [current, setCurrent] = useState<string | null>(null);

  const props = useMemo(() => {
    const list = doc?.dictionary.Properties ?? [];
    const f = filter.toLowerCase();
    return f ? list.filter((p) => p.Code.toLowerCase().includes(f) || p.Name.toLowerCase().includes(f)) : list;
  }, [doc, filter]);
  const sel = useListSelection(props.map((p) => p.Code));

  const usedBy = useMemo(() => {
    if (!doc || !current) return [];
    const d = doc.dictionary;
    return (d.Classes ?? []).filter((c) => (c.ClassProperties ?? []).some((cp) => cp.PropertyCode === current || internalCode(d, cp.PropertyUri, "prop") === current));
  }, [doc, current]);
  const classSel = useListSelection(usedBy.map((c) => c.Code));

  if (!opened || !doc) return null;

  const remove = async () => {
    if (!sel.selected.length) return;
    const ok = await askConfirm(t("Delete properties"), t("Delete {{n}} properties? All class properties using them are removed as well.", { n: sel.selected.length }), t("Delete"), true);
    if (ok) await attempt(() => op("prop.delete", { codes: sel.selected }));
  };
  const copy = () => {
    const list = (doc.dictionary.Properties ?? []).filter((p) => sel.selected.includes(p.Code));
    if (!list.length) return;
    copyProperties(list);
    notifyOk(t("{{n}} properties copied", { n: list.length }));
  };
  const paste = async () => {
    const clip = readClip("bsdd-properties");
    if (clip) await attempt(() => op("prop.paste", { payload: clip }));
  };
  const addToClass = async () => {
    if (!activeClass || !sel.selected.length) return;
    const n = await attempt(() => op<string[]>("cp.add_properties", { class_code: activeClass, property_codes: sel.selected, pset: activePset ?? undefined }));
    if (n) notifyOk(t("{{n}} class properties created", { n: n.length }));
  };
  const removeFromClasses = async () => {
    if (!current || !classSel.selected.length) return;
    await attempt(() => op("cp.remove_property_from_classes", { property_code: current, class_codes: classSel.selected }));
  };
  const onKeyDown = (e: React.KeyboardEvent) => {
    if ((e.target as HTMLElement).tagName === "INPUT") return;
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === "c") { e.preventDefault(); copy(); }
    else if (ctrl && e.key.toLowerCase() === "v") { e.preventDefault(); void paste(); }
    else if (e.key === "Delete") { e.preventDefault(); void remove(); }
  };
  const activeName = activeClass ? doc.dictionary.Classes?.find((c) => c.Code === activeClass)?.Name : null;

  return (
    <Modal opened onClose={close} title={t("Properties")} size="90%" styles={{ body: { height: "75vh", display: "flex", flexDirection: "column" } }}>
      <Group gap="xs" mb="xs">
        <TextInput placeholder={t("Filter…")} value={filter} onChange={(e) => setFilter(e.currentTarget.value)} style={{ flex: 1 }} />
        <Tooltip label={activeName ? t("Add selected properties to class '{{name}}'", { name: activeName }) : t("Select a class in the main window first")}>
          <ActionIcon variant="light" onClick={addToClass} disabled={!activeClass || !sel.selected.length}><IconSquarePlus size={16} /></ActionIcon>
        </Tooltip>
        <Tooltip label={t("New property")}><ActionIcon variant="light" onClick={() => openUi({ propertyEditor: {} })}><IconPlus size={16} /></ActionIcon></Tooltip>
      </Group>
      <div style={{ display: "flex", gap: 12, flex: 1, minHeight: 0 }}>
        <div style={{ flex: 2, overflow: "auto", border: "1px solid var(--mantine-color-default-border)" }} tabIndex={-1} onKeyDown={onKeyDown}>
          <table className="grid-table">
            <thead><tr><th>{t("Name")}</th><th>{t("Code")}</th><th>{t("Datatype")}</th><th>{t("Units")}</th></tr></thead>
            <tbody>
              {props.map((p) => (
                <tr
                  key={p.Code}
                  className={sel.selected.includes(p.Code) ? "selected" : ""}
                  onClick={(e) => { sel.click(p.Code, e); setCurrent(p.Code); }}
                  onDoubleClick={() => openUi({ propertyEditor: { code: p.Code } })}
                  draggable
                  onDragStart={(e) => setGraphDrag(e, (sel.selected.includes(p.Code) ? sel.selected : [p.Code]).map(propId))}
                  onContextMenu={(e) => {
                    sel.ensure(p.Code);
                    setCurrent(p.Code);
                    openMenu(e, [
                      { label: t("New"), icon: <IconPlus size={14} />, onClick: () => openUi({ propertyEditor: {} }) },
                      { label: t("Edit"), icon: <IconEdit size={14} />, onClick: () => openUi({ propertyEditor: { code: p.Code } }) },
                      { label: t("Add to active class"), icon: <IconSquarePlus size={14} />, onClick: addToClass, disabled: !activeClass },
                      divider,
                      { label: t("Copy"), icon: <IconCopy size={14} />, shortcut: "Ctrl+C", onClick: copy },
                      { label: t("Paste"), icon: <IconClipboard size={14} />, shortcut: "Ctrl+V", onClick: paste, disabled: !readClip("bsdd-properties") },
                      divider,
                      { label: t("Delete"), icon: <IconTrash size={14} />, color: "red", shortcut: "Del", onClick: remove },
                    ]);
                  }}
                >
                  <td>{p.Name}</td>
                  <td>{p.Code}</td>
                  <td>{p.DataType ?? ""}</td>
                  <td>{(p.Units ?? []).join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {props.length === 0 && <div className="empty-hint">{t("No properties")}</div>}
        </div>
        <div style={{ flex: 1, overflow: "auto", border: "1px solid var(--mantine-color-default-border)" }}>
          <table className="grid-table">
            <thead><tr><th colSpan={2}>{current ? t("Classes using '{{code}}'", { code: current }) : t("Classes using the property")}</th></tr></thead>
            <tbody>
              {usedBy.map((c) => (
                <tr
                  key={c.Code}
                  className={classSel.selected.includes(c.Code) ? "selected" : ""}
                  onClick={(e) => classSel.click(c.Code, e)}
                  draggable
                  onDragStart={(e) => setGraphDrag(e, (classSel.selected.includes(c.Code) ? classSel.selected : [c.Code]).map(classId))}
                  onDoubleClick={() => {
                    useProject.getState().setActiveClass(c.Code);
                    openUi({ revealClass: { code: c.Code, at: Date.now() } });
                    close();
                  }}
                  onContextMenu={(e) => {
                    classSel.ensure(c.Code);
                    openMenu(e, [{ label: t("Remove property from selected classes"), icon: <IconTrash size={14} />, color: "red", onClick: removeFromClasses }]);
                  }}
                >
                  <td>{c.Code}</td>
                  <td>{c.Name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Modal>
  );
}
