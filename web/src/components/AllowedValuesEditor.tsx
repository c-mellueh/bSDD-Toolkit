/** Editable table of allowed values (properties and class properties). */
import { ActionIcon, Alert, Badge, Button, Group, Menu, Modal, Stack, Switch, Table, Text, TextInput, Textarea, Tooltip } from "@mantine/core";
import { Toggle } from "./Toggle";
import {
  IconAlertTriangle,
  IconArrowsSort,
  IconClipboardList,
  IconCopy,
  IconDots,
  IconGripVertical,
  IconListNumbers,
  IconPlus,
  IconSearch,
  IconSortAZ,
  IconTrash,
} from "@tabler/icons-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { parseValuesText } from "../clipboard";
import { slugify, uniqueCode } from "../model";
import { notifyOk } from "../notify";
import { storageGet, storageSet, useSettings } from "../state/settings";
import type { AllowedValue } from "../types";

type Col = "Value" | "Code" | "Description" | "SortNumber" | "Uri" | "OwnedUri";

export function AllowedValuesEditor({ values, onChange, inherited }: { values: AllowedValue[]; onChange: (v: AllowedValue[]) => void; inherited?: AllowedValue[] }) {
  const { t } = useTranslation();
  const separator = useSettings((s) => s.pasteSeparator);
  const [quick, setQuick] = useState("");
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [showUris, setShowUris] = useState<boolean>(() => storageGet("bsdd-av-uris", false));
  const [pasteOpen, setPasteOpen] = useState(false);
  const [dragFrom, setDragFrom] = useState<number | null>(null);
  const [dragOver, setDragOver] = useState<number | null>(null);
  const table = useRef<HTMLTableElement | null>(null);

  const cols: Col[] = showUris ? ["Value", "Code", "Description", "SortNumber", "Uri", "OwnedUri"] : ["Value", "Code", "Description", "SortNumber"];
  const showInherited = values.length === 0 && (inherited?.length ?? 0) > 0;

  // validation
  const problems = useMemo(() => {
    const codeCount = new Map<string, number>();
    const valueCount = new Map<string, number>();
    for (const v of values) {
      codeCount.set(v.Code.trim().toLowerCase(), (codeCount.get(v.Code.trim().toLowerCase()) ?? 0) + 1);
      valueCount.set(v.Value.trim().toLowerCase(), (valueCount.get(v.Value.trim().toLowerCase()) ?? 0) + 1);
    }
    return values.map((v) => ({
      Value: !v.Value.trim() ? t("Value must not be empty") : (valueCount.get(v.Value.trim().toLowerCase()) ?? 0) > 1 ? t("Duplicate value") : null,
      Code: !v.Code.trim() ? t("Code must not be empty") : (codeCount.get(v.Code.trim().toLowerCase()) ?? 0) > 1 ? t("Duplicate code") : null,
    }));
  }, [values, t]);
  const nProblems = problems.filter((p) => p.Value || p.Code).length;

  const visible = useMemo(() => {
    const f = filter.trim().toLowerCase();
    return values.map((v, i) => ({ v, i })).filter(({ v }) => !f || [v.Value, v.Code, v.Description].some((x) => x?.toLowerCase().includes(f)));
  }, [values, filter]);

  const codesExcept = (i: number) => values.filter((_, j) => j !== i).map((v) => v.Code);
  const update = (i: number, patch: Partial<AllowedValue>) => {
    const next = values.slice();
    const old = next[i];
    const item = { ...old, ...patch };
    // keep the code in sync with the value as long as it was generated from it
    if (patch.Value !== undefined && (!old.Code || old.Code === slugify(old.Value) || old.Code === uniqueCode(slugify(old.Value) || "value", codesExcept(i)))) {
      item.Code = uniqueCode(slugify(patch.Value) || "value", codesExcept(i));
    }
    next[i] = item;
    onChange(next);
  };

  // focus a cell after the next render (new rows exist only then)
  const pendingFocus = useRef<{ row: number; col: Col } | null>(null);
  const focusNow = (row: number, col: Col) => table.current?.querySelector<HTMLInputElement>(`input[data-row="${row}"][data-col="${col}"]`)?.focus();
  const focusCell = (row: number, col: Col) => {
    if (row < values.length) focusNow(row, col);
    else pendingFocus.current = { row, col };
  };
  useEffect(() => {
    if (pendingFocus.current) {
      focusNow(pendingFocus.current.row, pendingFocus.current.col);
      pendingFocus.current = null;
    }
  });

  const addValues = (items: string[][], focus = false) => {
    const taken = new Set(values.map((v) => v.Code.toLowerCase()));
    const next = values.slice();
    let skipped = 0;
    for (const cols of items) {
      const value = cols[0]?.trim();
      if (!value) continue;
      let code = cols[1]?.trim() || slugify(value) || "value";
      if (taken.has(code.toLowerCase())) {
        if (cols[1]?.trim()) {
          skipped++;
          continue;
        }
        code = uniqueCode(code, [...taken]);
      }
      taken.add(code.toLowerCase());
      const sort = cols[3]?.trim();
      next.push({
        Value: value,
        Code: code,
        Description: cols[2]?.trim() || undefined,
        SortNumber: sort && !isNaN(Number(sort)) ? Number(sort) : undefined,
        OwnedUri: cols[4]?.trim() || undefined,
      });
    }
    onChange(next);
    if (focus) focusCell(next.length - 1, "Value");
    return { added: next.length - values.length, skipped };
  };

  const addEmpty = () => {
    // the code is generated from the value as soon as it is typed
    onChange([...values, { Code: "", Value: "" }]);
    focusCell(values.length, "Value");
  };
  const addQuick = () => {
    if (!quick.trim()) return addEmpty();
    addValues(quick.includes(";") || quick.includes("\t") ? parseValuesText(quick, separator) : [[quick]]);
    setQuick("");
  };

  const removeRows = (rows: number[]) => {
    const rm = new Set(rows);
    onChange(values.filter((_, i) => !rm.has(i)));
    setSelected(new Set());
  };
  const move = (from: number, to: number) => {
    if (from === to) return;
    const next = values.slice();
    const [item] = next.splice(from, 1);
    next.splice(to > from ? to - 1 : to, 0, item);
    onChange(next);
  };
  const sortAZ = () => onChange([...values].sort((a, b) => a.Value.localeCompare(b.Value, undefined, { numeric: true })));
  const sortBySortNumber = () => onChange([...values].sort((a, b) => (a.SortNumber ?? Infinity) - (b.SortNumber ?? Infinity)));
  const numberRows = () => onChange(values.map((v, i) => ({ ...v, SortNumber: i + 1 })));
  const regenerateCodes = () => {
    const taken: string[] = [];
    onChange(
      values.map((v) => {
        const code = uniqueCode(slugify(v.Value) || "value", taken);
        taken.push(code);
        return { ...v, Code: code };
      }),
    );
  };
  const copyAll = async () => {
    const text = values.map((v) => [v.Value, v.Code, v.Description ?? "", v.SortNumber ?? "", v.OwnedUri ?? ""].join("\t")).join("\n");
    await navigator.clipboard?.writeText(text);
    notifyOk(t("{{n}} values copied", { n: values.length }));
  };

  // pasting a list directly into the table
  const onPaste = (e: React.ClipboardEvent) => {
    const target = e.target as HTMLElement;
    const text = e.clipboardData.getData("text/plain");
    if (!text) return;
    const multi = text.includes("\n") || text.includes("\t") || text.includes(";");
    if (target.tagName === "INPUT" && !multi) return;
    if (target.tagName === "TEXTAREA") return;
    e.preventDefault();
    const res = addValues(parseValuesText(text, separator));
    notifyOk(t("{{n}} values added", { n: res.added }) + (res.skipped ? ` · ${t("{{n}} skipped (code exists)", { n: res.skipped })}` : ""));
  };

  const onCellKey = (e: React.KeyboardEvent<HTMLInputElement>, row: number, col: Col) => {
    const pos = visible.findIndex((x) => x.i === row);
    if (e.key === "Enter" || e.key === "ArrowDown") {
      e.preventDefault();
      if (pos < visible.length - 1) focusCell(visible[pos + 1].i, col);
      else if (e.key === "Enter" && !filter) addEmpty();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (pos > 0) focusCell(visible[pos - 1].i, col);
    }
  };

  const allSelected = visible.length > 0 && visible.every(({ i }) => selected.has(i));
  const toggleAll = () => setSelected(allSelected ? new Set() : new Set(visible.map(({ i }) => i)));
  const toggle = (i: number) =>
    setSelected((s) => {
      const n = new Set(s);
      if (n.has(i)) n.delete(i);
      else n.add(i);
      return n;
    });

  const header: Record<Col, string> = {
    Value: t("Value"),
    Code: t("Code"),
    Description: t("Description"),
    SortNumber: t("Sort"),
    Uri: "URI",
    OwnedUri: t("Owned URI"),
  };
  const cellValue = (v: AllowedValue, c: Col) => (c === "SortNumber" ? (v.SortNumber?.toString() ?? "") : ((v[c] as string | undefined) ?? ""));
  const setCell = (i: number, c: Col, x: string) =>
    update(i, c === "SortNumber" ? { SortNumber: x === "" || isNaN(Number(x)) ? undefined : Number(x) } : c === "Value" || c === "Code" ? { [c]: x } : { [c]: x || undefined });

  return (
    <div onPaste={onPaste} className="av-editor">
      <Group gap="xs" mb="xs" wrap="wrap">
        <TextInput
          style={{ flex: "1 1 220px" }}
          placeholder={t("Add a value and press Enter…")}
          value={quick}
          onChange={(e) => setQuick(e.currentTarget.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addQuick();
            }
          }}
          rightSection={<ActionIcon variant="filled" size="sm" onClick={addQuick} aria-label={t("Add value")}><IconPlus size={14} /></ActionIcon>}
        />
        <Button variant="default" leftSection={<IconClipboardList size={16} />} onClick={() => setPasteOpen(true)}>{t("Paste list…")}</Button>
        {values.length > 8 && (
          <TextInput style={{ flex: "0 1 200px" }} leftSection={<IconSearch size={14} />} placeholder={t("Filter…")} value={filter} onChange={(e) => setFilter(e.currentTarget.value)} />
        )}
        <Menu position="bottom-end" shadow="md">
          <Menu.Target><ActionIcon variant="default" size="lg" aria-label={t("More")}><IconDots size={16} /></ActionIcon></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconSortAZ size={14} />} onClick={sortAZ} disabled={values.length < 2}>{t("Sort A–Z")}</Menu.Item>
            <Menu.Item leftSection={<IconArrowsSort size={14} />} onClick={sortBySortNumber} disabled={values.length < 2}>{t("Sort by sort number")}</Menu.Item>
            <Menu.Item leftSection={<IconListNumbers size={14} />} onClick={numberRows} disabled={!values.length}>{t("Number in current order")}</Menu.Item>
            <Menu.Item onClick={regenerateCodes} disabled={!values.length}>{t("Regenerate codes from values")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconCopy size={14} />} onClick={copyAll} disabled={!values.length}>{t("Copy as table")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconTrash size={14} />} color="red" onClick={() => removeRows(values.map((_, i) => i))} disabled={!values.length}>{t("Remove all")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
      </Group>

      <Group justify="space-between" mb={6} wrap="wrap" gap="xs">
        <Group gap="xs">
          <Text size="sm" c="dimmed">{t("{{n}} values", { n: values.length })}</Text>
          {nProblems > 0 && <Badge color="red" variant="light" leftSection={<IconAlertTriangle size={12} />}>{t("{{n}} problems", { n: nProblems })}</Badge>}
          {selected.size > 0 && (
            <Button size="compact-sm" color="red" variant="light" leftSection={<IconTrash size={14} />} onClick={() => removeRows([...selected])}>
              {t("Remove {{n}} selected", { n: selected.size })}
            </Button>
          )}
        </Group>
        <Switch size="xs" label={t("Show URI columns")} checked={showUris} onChange={(e) => { setShowUris(e.currentTarget.checked); storageSet("bsdd-av-uris", e.currentTarget.checked); }} />
      </Group>

      {showInherited && (
        <Alert variant="light" color="gray" mb="xs" p="xs">
          <Group justify="space-between" wrap="nowrap">
            <Text size="sm">{t("{{n}} values are inherited from the property. Add values here to override them.", { n: inherited!.length })}</Text>
            <Button size="compact-sm" variant="light" onClick={() => onChange(inherited!.map((v) => ({ ...v })))}>{t("Copy to edit")}</Button>
          </Group>
        </Alert>
      )}

      <div className="av-table-wrap">
        <Table ref={table} className="av-table" verticalSpacing={0} horizontalSpacing={0} highlightOnHover stickyHeader>
          <Table.Thead>
            <Table.Tr>
              <Table.Th w={28} />
              <Table.Th w={32}><Toggle size="xs" checked={allSelected} indeterminate={!allSelected && selected.size > 0} onChange={toggleAll} aria-label={t("Select all")} /></Table.Th>
              {cols.map((c) => <Table.Th key={c} style={c === "SortNumber" ? { width: 70 } : undefined}>{header[c]}</Table.Th>)}
              <Table.Th w={36} />
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {showInherited &&
              inherited!.map((v, i) => (
                <Table.Tr key={`inh-${i}`} className="av-inherited">
                  <Table.Td />
                  <Table.Td />
                  {cols.map((c) => <Table.Td key={c}><span className="av-static">{cellValue(v, c)}</span></Table.Td>)}
                  <Table.Td />
                </Table.Tr>
              ))}
            {visible.map(({ v, i }) => (
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
                      e.dataTransfer.setData("text/x-bsdd-av", String(i));
                    }}
                    onDragEnd={() => { setDragFrom(null); setDragOver(null); }}
                    title={filter ? undefined : t("Drag to reorder")}
                  >
                    <IconGripVertical size={14} />
                  </span>
                </Table.Td>
                <Table.Td><Toggle size="xs" checked={selected.has(i)} onChange={() => toggle(i)} aria-label={t("Select")} /></Table.Td>
                {cols.map((c) => {
                  const err = c === "Value" || c === "Code" ? problems[i]?.[c] : null;
                  const input = (
                    <input
                      className={`av-input${err ? " av-error" : ""}${c === "Code" ? " mono" : ""}`}
                      data-row={i}
                      data-col={c}
                      value={cellValue(v, c)}
                      placeholder={c === "Value" ? t("Value") : undefined}
                      inputMode={c === "SortNumber" ? "numeric" : undefined}
                      onChange={(e) => setCell(i, c, e.currentTarget.value)}
                      onKeyDown={(e) => onCellKey(e, i, c)}
                    />
                  );
                  return (
                    <Table.Td key={c}>
                      <Tooltip label={err ?? ""} color="red" position="top-start" disabled={!err}>{input}</Tooltip>
                    </Table.Td>
                  );
                })}
                <Table.Td>
                  <ActionIcon size="sm" variant="subtle" color="red" onClick={() => removeRows([i])} aria-label={t("Remove")}><IconTrash size={14} /></ActionIcon>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
        {values.length === 0 && !showInherited && (
          <Stack align="center" gap={4} p="lg">
            <Text size="sm" c="dimmed">{t("No allowed values – the property accepts any value.")}</Text>
            <Text size="xs" c="dimmed">{t("Type a value above, or paste a list (also from Excel) anywhere in this table.")}</Text>
          </Stack>
        )}
        {values.length > 0 && visible.length === 0 && <Text size="sm" c="dimmed" p="md" ta="center">{t("Nothing found")}</Text>}
      </div>

      <PasteDialog opened={pasteOpen} onClose={() => setPasteOpen(false)} separator={separator} onAdd={(rows) => addValues(rows)} />
    </div>
  );
}

function PasteDialog({ opened, onClose, onAdd, separator }: { opened: boolean; onClose: () => void; onAdd: (rows: string[][]) => { added: number; skipped: number }; separator: string }) {
  const { t } = useTranslation();
  const [text, setText] = useState("");
  const rows = useMemo(() => (text.trim() ? parseValuesText(text, separator).filter((r) => r[0]) : []), [text, separator]);
  const add = () => {
    const res = onAdd(rows);
    notifyOk(t("{{n}} values added", { n: res.added }) + (res.skipped ? ` · ${t("{{n}} skipped (code exists)", { n: res.skipped })}` : ""));
    setText("");
    onClose();
  };
  return (
    <Modal opened={opened} onClose={onClose} title={t("Paste list of values")} size="lg" zIndex={400}>
      <Stack gap="xs">
        <Text size="sm" c="dimmed">
          {t("One value per line, or columns separated by ';' or tabs (e.g. copied from Excel): Value; Code; Description; Sort number; Owned URI. Missing codes are generated.")}
        </Text>
        <Textarea autosize minRows={6} maxRows={14} value={text} onChange={(e) => setText(e.currentTarget.value)} data-autofocus placeholder={"Beton\nStahl\nHolz"} className="mono" />
        {rows.length > 0 && (
          <div style={{ maxHeight: 220, overflow: "auto", border: "1px solid var(--mantine-color-default-border)", borderRadius: 6 }}>
            <Table fz="xs" verticalSpacing={2} stickyHeader>
              <Table.Thead><Table.Tr><Table.Th>{t("Value")}</Table.Th><Table.Th>{t("Code")}</Table.Th><Table.Th>{t("Description")}</Table.Th><Table.Th>{t("Sort")}</Table.Th></Table.Tr></Table.Thead>
              <Table.Tbody>
                {rows.slice(0, 200).map((r, i) => (
                  <Table.Tr key={i}><Table.Td>{r[0]}</Table.Td><Table.Td c={r[1] ? undefined : "dimmed"}>{r[1] || slugify(r[0])}</Table.Td><Table.Td>{r[2]}</Table.Td><Table.Td>{r[3]}</Table.Td></Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          </div>
        )}
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose}>{t("Cancel")}</Button>
          <Button onClick={add} disabled={!rows.length}>{t("Add {{n}} values", { n: rows.length })}</Button>
        </Group>
      </Stack>
    </Modal>
  );
}
