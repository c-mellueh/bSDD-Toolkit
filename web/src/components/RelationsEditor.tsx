/* eslint-disable @typescript-eslint/no-explicit-any */
/** Editable table of class / property relations. */
import { ActionIcon, Anchor, Autocomplete, Badge, Button, Group, Menu, Modal, NumberInput, Select, Stack, Switch, Table, Text, TextInput, Textarea, Tooltip } from "@mantine/core";
import { IconAlertTriangle, IconClipboardList, IconCopy, IconDots, IconExternalLink, IconGripVertical, IconPlus, IconSearch, IconSortAZ, IconTrash, IconWorld } from "@tabler/icons-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { EDGE_STYLE, type EdgeKind } from "../graph/model";
import { CLASS_RELATION_TYPES, PROPERTY_RELATION_TYPES, internalCode, isUri } from "../model";
import { notifyOk } from "../notify";
import { openClass, openProperty } from "../state/nav";
import { useProject } from "../state/project";
import { storageGet, storageSet, useSettings } from "../state/settings";
import type { ClassRelation, PropertyRelation } from "../types";
import { Toggle } from "./Toggle";

type AnyRelation = ClassRelation | PropertyRelation;
type Status = "internal" | "external" | "unknown";

export function RelationsEditor({ kind, relations, onChange, selfCode }: { kind: "class" | "property"; relations: AnyRelation[]; onChange: (r: AnyRelation[]) => void; selfCode?: string }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const allowUnknown = useSettings((s) => s.allowUnknownUri);
  const [type, setType] = useState<string>("IsSimilarTo");
  const [target, setTarget] = useState("");
  const [fraction, setFraction] = useState<number | null>(null);
  const [owned, setOwned] = useState("");
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [showUris, setShowUris] = useState<boolean>(() => storageGet("bsdd-rel-uris", false));
  const [pasteOpen, setPasteOpen] = useState(false);
  const [dragFrom, setDragFrom] = useState<number | null>(null);
  const [dragOver, setDragOver] = useState<number | null>(null);
  const d = doc?.dictionary;
  const useOwnUri = !!d?.UseOwnUri;
  const types = kind === "class" ? CLASS_RELATION_TYPES : PROPERTY_RELATION_TYPES;
  const uriKey = kind === "class" ? "RelatedClassUri" : "RelatedPropertyUri";
  const nameKey = kind === "class" ? "RelatedClassName" : "RelatedPropertyName";
  const ikind = kind === "class" ? "class" : "prop";

  const options = useMemo(() => {
    if (!d) return [];
    if (kind === "class") {
      return (d.Classes ?? [])
        .filter((c) => c.Code !== selfCode && (type !== "HasMaterial" || c.ClassType === "Material"))
        .map((c) => ({ value: c.Code, label: `${c.Name} (${c.Code})` }));
    }
    return (d.Properties ?? []).filter((p) => p.Code !== selfCode).map((p) => ({ value: p.Code, label: `${p.Name} (${p.Code})` }));
  }, [d, kind, type, selfCode]);

  /** Resolve a code or URI: internal item code, external URI or unknown. */
  const resolve = (ref: string): { status: Status; code?: string } => {
    if (!ref || !d) return { status: "unknown" };
    const has = (c: string) => (kind === "class" ? idx.classes.has(c) : idx.properties.has(c));
    if (has(ref)) return { status: "internal", code: ref };
    if (isUri(ref)) {
      const code = internalCode(d, ref, ikind);
      if (code && has(code)) return { status: "internal", code };
      return { status: allowUnknown || ref.includes("/uri/") ? "external" : "unknown" };
    }
    return { status: "unknown" };
  };
  const nameOf = (r: any, code?: string) => {
    if (code) return (kind === "class" ? idx.classes.get(code)?.Name : idx.properties.get(code)?.Name) ?? code;
    const uri: string = r[uriKey] ?? "";
    return r[nameKey] || (isUri(uri) ? uri.split("/").pop() : uri);
  };
  // the option label was picked from the autocomplete → take the code
  const targetRef = options.find((o) => o.label === target)?.value ?? target.trim();
  const targetStatus = resolve(targetRef).status;
  const targetValid = !!targetRef && targetStatus !== "unknown";

  const rows = useMemo(
    () =>
      relations.map((r: any) => {
        const ref = r[uriKey] ?? "";
        return { r, ref, ...resolve(ref) };
      }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [relations, idx, d, allowUnknown],
  );
  const problems = useMemo(() => {
    const seen = new Map<string, number>();
    for (const x of rows) {
      const key = `${x.r.RelationType}|${x.code ?? x.ref}`;
      seen.set(key, (seen.get(key) ?? 0) + 1);
    }
    return rows.map((x) => {
      if (x.status === "unknown") return t("Unknown target");
      if (x.code && x.code === selfCode) return t("Relation to itself");
      if ((seen.get(`${x.r.RelationType}|${x.code ?? x.ref}`) ?? 0) > 1) return t("Duplicate relation");
      return null;
    });
  }, [rows, selfCode, t]);
  const nProblems = problems.filter(Boolean).length;

  const visible = useMemo(() => {
    const f = filter.trim().toLowerCase();
    return rows.map((x, i) => ({ ...x, i })).filter((x) => !f || [x.r.RelationType, x.ref, nameOf(x.r, x.code)].some((s) => String(s ?? "").toLowerCase().includes(f)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rows, filter]);

  const make = (relType: string, ref: string, extra?: { fraction?: number | null; owned?: string }) => {
    const rel: any = { RelationType: relType, [uriKey]: ref };
    if (kind === "class" && relType === "HasMaterial" && extra?.fraction != null) rel.Fraction = extra.fraction;
    if (extra?.owned) rel.OwnedUri = extra.owned;
    return rel as AnyRelation;
  };
  const add = () => {
    if (!targetValid) return;
    onChange([...relations, make(type, targetRef, { fraction, owned: useOwnUri ? owned : undefined })]);
    setTarget("");
    setFraction(null);
    setOwned("");
  };
  const update = (i: number, patch: Record<string, any>) => {
    const next = relations.slice();
    const item: any = { ...next[i], ...patch };
    for (const [k, v] of Object.entries(patch)) if (v === undefined || v === "" || v === null) delete item[k];
    if (item.RelationType !== "HasMaterial") delete item.Fraction;
    next[i] = item;
    onChange(next);
  };
  const removeRows = (list: number[]) => {
    const rm = new Set(list);
    onChange(relations.filter((_, i) => !rm.has(i)));
    setSelected(new Set());
  };
  const move = (from: number, to: number) => {
    if (from === to) return;
    const next = relations.slice();
    const [item] = next.splice(from, 1);
    next.splice(to > from ? to - 1 : to, 0, item);
    onChange(next);
  };
  const sortBy = (fn: (x: (typeof rows)[number]) => string) => {
    const order = rows.map((x, i) => ({ x, i })).sort((a, b) => fn(a.x).localeCompare(fn(b.x), undefined, { numeric: true }));
    onChange(order.map(({ i }) => relations[i]));
  };
  const copyAll = async () => {
    const text = rows.map((x) => [x.r.RelationType, nameOf(x.r, x.code), x.ref, (x.r as any).Fraction ?? "", x.r.OwnedUri ?? ""].join("\t")).join("\n");
    await navigator.clipboard?.writeText(text);
    notifyOk(t("{{n}} relations copied", { n: rows.length }));
  };
  const addMany = (relType: string, refs: string[]) => {
    const existing = new Set(rows.map((x) => `${x.r.RelationType}|${x.code ?? x.ref}`));
    const next = relations.slice();
    let skipped = 0;
    for (const raw of refs) {
      const ref = raw.trim();
      if (!ref) continue;
      const res = resolve(ref);
      const key = `${relType}|${res.code ?? ref}`;
      if (res.status === "unknown" || existing.has(key) || res.code === selfCode) {
        skipped++;
        continue;
      }
      existing.add(key);
      next.push(make(relType, ref));
    }
    onChange(next);
    return { added: next.length - relations.length, skipped };
  };

  const allSelected = visible.length > 0 && visible.every((x) => selected.has(x.i));
  const toggle = (i: number) =>
    setSelected((s) => {
      const n = new Set(s);
      if (n.has(i)) n.delete(i);
      else n.add(i);
      return n;
    });
  const showOwned = useOwnUri || showUris;
  const color = (relType: string) => EDGE_STYLE[relType as EdgeKind]?.color ?? "var(--mantine-color-gray-6)";
  const typeData = types.map((x) => ({ value: x, label: t(x) }));
  const renderType = ({ option }: { option: { value: string; label: string } }) => (
    <Group gap={8} wrap="nowrap"><span className="rel-dot" style={{ background: color(option.value) }} />{option.label}</Group>
  );

  return (
    <div className="av-editor">
      {/* add bar */}
      <div className="rel-addbar">
        <Select
          data={typeData}
          value={type}
          onChange={(v) => setType(v ?? type)}
          allowDeselect={false}
          w={170}
          renderOption={renderType}
          leftSection={<span className="rel-dot" style={{ background: color(type) }} />}
          aria-label={t("Relation")}
          comboboxProps={{ zIndex: 400 }}
        />
        <Autocomplete
          data={options}
          value={target}
          onChange={setTarget}
          placeholder={kind === "class" ? t("Target class: name, code or URI…") : t("Target property: name, code or URI…")}
          style={{ flex: "1 1 240px" }}
          limit={50}
          error={target && !targetValid ? true : undefined}
          leftSection={target && targetStatus === "external" ? <IconWorld size={14} /> : undefined}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          comboboxProps={{ zIndex: 400 }}
        />
        {kind === "class" && type === "HasMaterial" && (
          <NumberInput placeholder={t("Fraction")} value={fraction ?? ""} onChange={(v) => setFraction(v === "" ? null : Number(v))} w={110} min={0} max={1} step={0.1} decimalScale={4} />
        )}
        {useOwnUri && <TextInput placeholder={t("Owned URI")} value={owned} onChange={(e) => setOwned(e.currentTarget.value)} w={180} />}
        <Button leftSection={<IconPlus size={16} />} onClick={add} disabled={!targetValid}>{t("Add")}</Button>
        <Tooltip label={t("Paste list…")}>
          <ActionIcon variant="default" size="lg" onClick={() => setPasteOpen(true)} aria-label={t("Paste list…")}><IconClipboardList size={16} /></ActionIcon>
        </Tooltip>
        <Menu position="bottom-end" shadow="md">
          <Menu.Target><ActionIcon variant="default" size="lg" aria-label={t("More")}><IconDots size={16} /></ActionIcon></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconSortAZ size={14} />} onClick={() => sortBy((x) => `${x.r.RelationType}|${nameOf(x.r, x.code)}`)} disabled={rows.length < 2}>{t("Sort by relation type")}</Menu.Item>
            <Menu.Item leftSection={<IconSortAZ size={14} />} onClick={() => sortBy((x) => String(nameOf(x.r, x.code)))} disabled={rows.length < 2}>{t("Sort by target")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconCopy size={14} />} onClick={copyAll} disabled={!rows.length}>{t("Copy as table")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconTrash size={14} />} color="red" onClick={() => removeRows(rows.map((_, i) => i))} disabled={!rows.length}>{t("Remove all")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
      </div>
      {target && !targetValid && <Text size="xs" c="red" mt={-4} mb={6}>{t("Unknown code. Pick an entry from the list or enter a bSDD URI.")}</Text>}

      <Group justify="space-between" mb={6} wrap="wrap" gap="xs">
        <Group gap="xs">
          <Text size="sm" c="dimmed">{t("{{n}} relations", { n: rows.length })}</Text>
          {nProblems > 0 && <Badge color="red" variant="light" leftSection={<IconAlertTriangle size={12} />}>{t("{{n}} problems", { n: nProblems })}</Badge>}
          {selected.size > 0 && (
            <Button size="compact-sm" color="red" variant="light" leftSection={<IconTrash size={14} />} onClick={() => removeRows([...selected])}>
              {t("Remove {{n}} selected", { n: selected.size })}
            </Button>
          )}
        </Group>
        <Group gap="sm">
          {rows.length > 8 && <TextInput size="xs" w={180} leftSection={<IconSearch size={12} />} placeholder={t("Filter…")} value={filter} onChange={(e) => setFilter(e.currentTarget.value)} />}
          {!useOwnUri && <Switch size="xs" label={t("Show URI columns")} checked={showUris} onChange={(e) => { setShowUris(e.currentTarget.checked); storageSet("bsdd-rel-uris", e.currentTarget.checked); }} />}
        </Group>
      </Group>

      <div className="av-table-wrap">
        <Table className="av-table" verticalSpacing={0} horizontalSpacing={0} highlightOnHover stickyHeader>
          <Table.Thead>
            <Table.Tr>
              <Table.Th w={28} />
              <Table.Th w={50}><Toggle size="xs" checked={allSelected} indeterminate={!allSelected && selected.size > 0} onChange={() => setSelected(allSelected ? new Set() : new Set(visible.map((x) => x.i)))} aria-label={t("Select all")} /></Table.Th>
              <Table.Th style={{ width: 170 }}>{t("Relation")}</Table.Th>
              <Table.Th>{t("Target")}</Table.Th>
              <Table.Th>{t("URI / Code")}</Table.Th>
              {kind === "class" && <Table.Th style={{ width: 90 }}>{t("Fraction")}</Table.Th>}
              {showOwned && <Table.Th>{t("Owned URI")}</Table.Th>}
              <Table.Th w={36} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {visible.map(({ r, ref, status, code, i }) => {
              const err = problems[i];
              const rel = r as any;
              return (
                <Table.Tr
                  key={i}
                  className={`${selected.has(i) ? "av-selected" : ""}${dragOver === i && dragFrom !== null ? " av-drop" : ""}`}
                  onDragOver={(e) => {
                    if (dragFrom === null) return;
                    e.preventDefault();
                    setDragOver(i);
                  }}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (dragFrom !== null) move(dragFrom, i > dragFrom ? i + 1 : i);
                    setDragFrom(null);
                    setDragOver(null);
                  }}
                >
                  <Table.Td>
                    <span
                      className="av-grip"
                      draggable={!filter}
                      onDragStart={(e) => {
                        setDragFrom(i);
                        e.dataTransfer.effectAllowed = "move";
                        e.dataTransfer.setData("text/x-bsdd-rel", String(i));
                      }}
                      onDragEnd={() => { setDragFrom(null); setDragOver(null); }}
                      title={filter ? undefined : t("Drag to reorder")}
                    >
                      <IconGripVertical size={14} />
                    </span>
                  </Table.Td>
                  <Table.Td><Toggle size="xs" checked={selected.has(i)} onChange={() => toggle(i)} aria-label={t("Select")} /></Table.Td>
                  <Table.Td>
                    <Select
                      className="rel-type"
                      variant="unstyled"
                      size="xs"
                      data={typeData}
                      value={r.RelationType}
                      onChange={(v) => v && update(i, { RelationType: v })}
                      allowDeselect={false}
                      renderOption={renderType}
                      leftSection={<span className="rel-dot" style={{ background: color(r.RelationType) }} />}
                      comboboxProps={{ zIndex: 400 }}
                    />
                  </Table.Td>
                  <Table.Td>
                    <Group gap={6} wrap="nowrap" px={8} style={{ minWidth: 0 }}>
                      {status === "internal" && code ? (
                        <Anchor size="sm" truncate onClick={() => (kind === "class" ? openClass(code) : openProperty(code))}>{nameOf(r, code)}</Anchor>
                      ) : status === "external" ? (
                        <>
                          <IconWorld size={14} style={{ flex: "none", opacity: 0.6 }} />
                          <Anchor size="sm" truncate href={ref} target="_blank" rel="noreferrer">{nameOf(r)}</Anchor>
                          <IconExternalLink size={12} style={{ flex: "none", opacity: 0.5 }} />
                        </>
                      ) : (
                        <Text size="sm" c="red" truncate>{nameOf(r) || "—"}</Text>
                      )}
                      {err && (
                        <Tooltip label={err} color="red"><IconAlertTriangle size={14} color="var(--mantine-color-red-6)" style={{ flex: "none" }} /></Tooltip>
                      )}
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <input
                      className={`av-input mono${status === "unknown" ? " av-error" : ""}`}
                      value={ref}
                      title={ref}
                      onChange={(e) => update(i, { [uriKey]: e.currentTarget.value, [nameKey]: undefined })}
                    />
                  </Table.Td>
                  {kind === "class" && (
                    <Table.Td>
                      {r.RelationType === "HasMaterial" ? (
                        <input
                          className="av-input"
                          inputMode="decimal"
                          value={rel.Fraction ?? ""}
                          placeholder="0–1"
                          onChange={(e) => {
                            const v = e.currentTarget.value.replace(",", ".");
                            update(i, { Fraction: v === "" || isNaN(Number(v)) ? undefined : Number(v) });
                          }}
                        />
                      ) : (
                        <span className="av-static" style={{ opacity: 0.3 }}>–</span>
                      )}
                    </Table.Td>
                  )}
                  {showOwned && (
                    <Table.Td><input className="av-input mono" value={r.OwnedUri ?? ""} onChange={(e) => update(i, { OwnedUri: e.currentTarget.value || undefined })} /></Table.Td>
                  )}
                  <Table.Td>
                    <ActionIcon size="sm" variant="subtle" color="red" onClick={() => removeRows([i])} aria-label={t("Remove")}><IconTrash size={14} /></ActionIcon>
                  </Table.Td>
                </Table.Tr>
              );
            })}
          </Table.Tbody>
        </Table>
        {rows.length === 0 && (
          <Stack align="center" gap={4} p="lg">
            <Text size="sm" c="dimmed">{t("No relations")}</Text>
            <Text size="xs" c="dimmed">
              {kind === "class" ? t("Link this class to other classes of this or another bSDD dictionary.") : t("Link this property to other properties of this or another bSDD dictionary.")}
            </Text>
          </Stack>
        )}
        {rows.length > 0 && visible.length === 0 && <Text size="sm" c="dimmed" p="md" ta="center">{t("Nothing found")}</Text>}
      </div>

      <PasteDialog opened={pasteOpen} onClose={() => setPasteOpen(false)} types={typeData} renderType={renderType} initialType={type} onAdd={addMany} kind={kind} />
    </div>
  );
}

function PasteDialog(props: {
  opened: boolean;
  onClose: () => void;
  types: { value: string; label: string }[];
  renderType: (o: { option: { value: string; label: string } }) => React.ReactNode;
  initialType: string;
  kind: "class" | "property";
  onAdd: (type: string, refs: string[]) => { added: number; skipped: number };
}) {
  const { t } = useTranslation();
  const [text, setText] = useState("");
  const [type, setType] = useState(props.initialType);
  const refs = text.split(/[\n;\t]/).map((s) => s.trim()).filter(Boolean);
  const add = () => {
    const res = props.onAdd(type, refs);
    notifyOk(t("{{n}} relations added", { n: res.added }) + (res.skipped ? ` · ${t("{{n}} skipped", { n: res.skipped })}` : ""));
    setText("");
    props.onClose();
  };
  return (
    <Modal opened={props.opened} onClose={props.onClose} title={t("Add several relations")} size="lg" zIndex={400}>
      <Stack gap="xs">
        <Select label={t("Relation")} data={props.types} value={type} onChange={(v) => setType(v ?? type)} allowDeselect={false} renderOption={props.renderType} comboboxProps={{ zIndex: 500 }} />
        <Textarea
          label={props.kind === "class" ? t("Target classes") : t("Target properties")}
          description={t("One code or bSDD URI per line. Unknown, duplicate and self references are skipped.")}
          autosize
          minRows={6}
          maxRows={14}
          value={text}
          onChange={(e) => setText(e.currentTarget.value)}
          className="mono"
          data-autofocus
        />
        <Group justify="flex-end">
          <Button variant="default" onClick={props.onClose}>{t("Cancel")}</Button>
          <Button onClick={add} disabled={!refs.length}>{t("Add {{n}} relations", { n: refs.length })}</Button>
        </Group>
      </Stack>
    </Modal>
  );
}
