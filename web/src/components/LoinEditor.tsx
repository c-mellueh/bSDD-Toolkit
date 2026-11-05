import { ActionIcon, Badge, Button, FileButton, Grid, Group, Modal, Select, Stack, Switch, Tabs, Text, TextInput, Tooltip } from "@mantine/core";
import { Toggle } from "./Toggle";
import { IconArrowDown, IconArrowUp, IconArrowsMaximize, IconArrowsMinimize, IconChevronDown, IconChevronRight, IconDownload, IconPencil, IconPlus, IconSearch, IconTrash, IconUpload } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { downloadFile, readFileText } from "../api";
import { GOP, cpName } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { useUi } from "../state/ui";
import type { BsddClass, ClassProperty, LoinActor, LoinEntry, LoinSpec } from "../types";
import { askConfirm, askText } from "./dialogs";

export const specKey = (p: string, m: string) => `${p}|${m}`;

export function LoinEditor({ inline }: { inline?: boolean } = {}) {
  const { t } = useTranslation();
  const opened = useUi((s) => s.loin) || !!inline;
  const close = () => useUi.getState().set({ loin: false });
  const doc = useProject((s) => s.doc);
  const projectId = useProject((s) => s.projectId);
  const loin = doc?.extras.loin;
  const [purpose, setPurpose] = useState<string | null>(null);
  const [milestone, setMilestone] = useState<string | null>(null);
  const [current, setCurrent] = useState<string | null>(null);
  const [recursive, setRecursive] = useState(true);

  useEffect(() => {
    if (opened && loin && !loin.purposes?.length) void op("loin.init");
  }, [opened, loin]);

  const purposes = loin?.purposes ?? [];
  const milestones = loin?.milestones ?? [];
  const p = purposes.find((x) => x.guid === purpose)?.guid ?? purposes[0]?.guid ?? null;
  const m = milestones.find((x) => x.guid === milestone)?.guid ?? milestones[0]?.guid ?? null;
  const key = p && m ? specKey(p, m) : null;
  const spec = key ? loin?.specs?.[key] : undefined;

  if (!opened || !doc || !loin) return null;

  const importXml = async (file: File | null) => {
    if (!file) return;
    const xml = await readFileText(file);
    const n = await attempt(() => op<number>("loin.import_xml", { xml }));
    if (n !== undefined) notifyOk(t("{{n}} specifications imported", { n }));
  };

  return (
    <Wrap inline={inline} close={close} title={t("Level of Information Need (ISO 7817-3)")}>
      <Tabs defaultValue="selection" style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
        <Tabs.List mb="sm">
          <Tabs.Tab value="selection">{t("Specifications")}</Tabs.Tab>
          <Tabs.Tab value="setup">{t("Purposes, milestones & actors")}</Tabs.Tab>
          <Group gap="xs" ml="auto">
            <FileButton onChange={importXml} accept=".xml,application/xml">
              {(props) => <Button {...props} variant="default" leftSection={<IconUpload size={14} />}>{t("Import XML")}</Button>}
            </FileButton>
            <Button variant="default" leftSection={<IconDownload size={14} />} onClick={() => attempt(() => downloadFile(`/api/projects/${projectId}/export/iso7817`, { specs: null }))}>{t("Export XML")}</Button>
          </Group>
        </Tabs.List>
        <Tabs.Panel value="selection" style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
          <Group gap="sm" mb="sm" align="flex-end" wrap="wrap">
            <Select label={t("Purpose")} data={purposes.map((x) => ({ value: x.guid, label: x.name }))} value={p} onChange={setPurpose} allowDeselect={false} w={220} />
            <Select label={t("Milestone")} data={milestones.map((x) => ({ value: x.guid, label: x.name }))} value={m} onChange={setMilestone} allowDeselect={false} w={220} />
            <Switch label={t("Apply to child classes")} checked={recursive} onChange={(e) => setRecursive(e.currentTarget.checked)} mb={8} />
          </Group>
          {key ? (
            <div className="loin-grid">
              <ClassPanel specKey={key} spec={spec} recursive={recursive} current={current} setCurrent={setCurrent} />
              <ClassPropsPanel specKey={key} spec={spec} classCode={current} />
              <PsetPanel specKey={key} spec={spec} />
            </div>
          ) : (
            <Text c="dimmed">{t("Add a purpose and a milestone first.")}</Text>
          )}
        </Tabs.Panel>
        <Tabs.Panel value="setup" style={{ overflow: "auto", minHeight: 0 }}>
          <Grid>
            <Grid.Col span={{ base: 12, md: 6 }}><EntryList kind="purpose" title={t("Purposes")} items={purposes} /></Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}><EntryList kind="milestone" title={t("Milestones")} items={milestones} /></Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}><ActorForm which="providing" title={t("Providing actor")} actor={loin.providing_actor} /></Grid.Col>
            <Grid.Col span={{ base: 12, md: 6 }}><ActorForm which="receiving" title={t("Receiving actor")} actor={loin.receiving_actor} /></Grid.Col>
          </Grid>
        </Tabs.Panel>
      </Tabs>
    </Wrap>
  );
}

// ------------------------------------------------------------------ shared bits

type Tri = "on" | "off" | "partial";
const triOf = (n: number, total: number): Tri => (n === 0 ? "off" : n >= total ? "on" : "partial");

function Panel({ title, subtitle, count, actions, filter, setFilter, children }: {
  title: string;
  subtitle?: React.ReactNode;
  count?: React.ReactNode;
  actions?: React.ReactNode;
  filter?: string;
  setFilter?: (v: string) => void;
  children: React.ReactNode;
}) {
  const { t } = useTranslation();
  return (
    <div className="loin-panel">
      <div className="loin-panel-header">
        <Group justify="space-between" wrap="nowrap" gap="xs">
          <div style={{ minWidth: 0 }}>
            <Text fw={600} truncate>{title}</Text>
            {subtitle && <Text size="xs" c="dimmed" truncate>{subtitle}</Text>}
          </div>
          <Group gap={4} wrap="nowrap">
            {count}
            {actions}
          </Group>
        </Group>
        {setFilter && (
          <TextInput mt={8} size="xs" leftSection={<IconSearch size={12} />} placeholder={t("Filter…")} value={filter} onChange={(e) => setFilter(e.currentTarget.value)} />
        )}
      </div>
      <div className="loin-panel-body">{children}</div>
    </div>
  );
}

function Chevron({ open, show, onClick }: { open: boolean; show: boolean; onClick: () => void }) {
  return (
    <span className="loin-chevron" onClick={(e) => { e.stopPropagation(); if (show) onClick(); }}>
      {show ? open ? <IconChevronDown size={14} /> : <IconChevronRight size={14} /> : null}
    </span>
  );
}

function useOpenSet(initial: string[] = []) {
  const [open, setOpen] = useState<Set<string>>(new Set(initial));
  const toggle = (k: string) =>
    setOpen((s) => {
      const n = new Set(s);
      if (n.has(k)) n.delete(k);
      else n.add(k);
      return n;
    });
  return { open, setOpen, toggle };
}

// ------------------------------------------------------------------ 1. classes

function ClassPanel({ specKey: key, spec, recursive, current, setCurrent }: { specKey: string; spec?: LoinSpec; recursive: boolean; current: string | null; setCurrent: (c: string) => void }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc)!;
  const idx = useProject((s) => s.idx);
  const [filter, setFilter] = useState("");
  const { open, setOpen, toggle } = useOpenSet();
  const included = useMemo(() => new Set(spec?.classes ?? []), [spec]);
  const classes = (doc.dictionary.Classes ?? []).filter((c) => c.ClassType !== GOP);
  const kidsOf = (code: string | null) =>
    code === null ? classes.filter((c) => !c.ParentClassCode || !idx.classes.has(c.ParentClassCode)) : (idx.children.get(code) ?? []).filter((c) => c.ClassType !== GOP);
  const setIncluded = (code: string, value: boolean) => attempt(() => op("loin.set_class_included", { spec: key, codes: [code], included: value, recursive }));
  const f = filter.trim().toLowerCase();
  const matches = (c: BsddClass) => !f || c.Name.toLowerCase().includes(f) || c.Code.toLowerCase().includes(f);
  // when filtering: show matching classes and their ancestors, expanded
  const visibleByFilter = useMemo(() => {
    if (!f) return null;
    const keep = new Set<string>();
    for (const c of classes) {
      if (!matches(c)) continue;
      let cur: BsddClass | undefined = c;
      while (cur && !keep.has(cur.Code)) {
        keep.add(cur.Code);
        cur = cur.ParentClassCode ? idx.classes.get(cur.ParentClassCode) : undefined;
      }
    }
    return keep;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [f, classes, idx]);

  const render = (parent: string | null, depth: number): React.ReactNode =>
    kidsOf(parent)
      .filter((c) => !visibleByFilter || visibleByFilter.has(c.Code))
      .map((c) => {
        const kids = kidsOf(c.Code);
        const isOpen = !!visibleByFilter || open.has(c.Code);
        const nProps = spec?.properties?.[c.Code]?.length ?? 0;
        const nAll = (c.ClassProperties ?? []).length;
        return (
          <div key={c.Code}>
            <div className={`loin-row${current === c.Code ? " active" : ""}`} style={{ paddingLeft: 6 + depth * 16 }} onClick={() => setCurrent(c.Code)}>
              <Chevron open={isOpen} show={kids.length > 0} onClick={() => toggle(c.Code)} />
              <span onClick={(e) => e.stopPropagation()}><Toggle size="xs" checked={included.has(c.Code)} onChange={(e) => setIncluded(c.Code, e.currentTarget.checked)} /></span>
              <span className="loin-name">{c.Name}</span>
              <span className="loin-code">{c.Code}</span>
              {included.has(c.Code) && nAll > 0 && (
                <Tooltip label={t("{{n}} of {{total}} properties selected", { n: nProps, total: nAll })}>
                  <Badge size="xs" variant="light" color={nProps ? "blue" : "gray"}>{nProps}/{nAll}</Badge>
                </Tooltip>
              )}
            </div>
            {isOpen && kids.length > 0 && render(c.Code, depth + 1)}
          </div>
        );
      });

  return (
    <Panel
      title={t("Classes")}
      subtitle={t("Which classes are required")}
      count={<Badge variant="light">{t("{{n}} included", { n: included.size })}</Badge>}
      actions={
        <>
          <Tooltip label={t("Expand all")}><ActionIcon size="sm" variant="subtle" onClick={() => setOpen(new Set(classes.map((c) => c.Code)))}><IconArrowsMaximize size={14} /></ActionIcon></Tooltip>
          <Tooltip label={t("Collapse all")}><ActionIcon size="sm" variant="subtle" onClick={() => setOpen(new Set())}><IconArrowsMinimize size={14} /></ActionIcon></Tooltip>
        </>
      }
      filter={filter}
      setFilter={setFilter}
    >
      {render(null, 0)}
      {classes.length === 0 && <div className="empty-hint">{t("No classes yet.")}</div>}
    </Panel>
  );
}

// ------------------------------------------------------------------ 2. properties of the selected class

function ClassPropsPanel({ specKey: key, spec, classCode }: { specKey: string; spec?: LoinSpec; classCode: string | null }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc)!;
  const idx = useProject((s) => s.idx);
  const { open, toggle } = useOpenSet();
  const cls = classCode ? idx.classes.get(classCode) : undefined;
  const checked = new Set((spec?.properties?.[classCode ?? ""] ?? []).map(([ps, c]) => `${ps}|${c}`));
  const groups = new Map<string, ClassProperty[]>();
  for (const cp of cls?.ClassProperties ?? []) {
    const ps = cp.PropertySet ?? "";
    if (!groups.has(ps)) groups.set(ps, []);
    groups.get(ps)!.push(cp);
  }
  const setProps = (items: [string, string][], value: boolean) =>
    classCode && attempt(() => op("loin.set_properties_included", { spec: key, class_code: classCode, items, included: value }));
  const allItems = [...groups.entries()].flatMap(([ps, cps]) => cps.map((cp) => [ps, cp.Code] as [string, string]));
  const tri = triOf(allItems.filter(([a, b]) => checked.has(`${a}|${b}`)).length, allItems.length);

  return (
    <Panel
      title={cls ? cls.Name : t("Properties of the class")}
      subtitle={cls ? t("Properties required for this class") : t("Select a class on the left")}
      count={cls && allItems.length > 0 ? <Badge variant="light">{checked.size}/{allItems.length}</Badge> : undefined}
      actions={
        cls && allItems.length > 0 ? (
          <Tooltip label={t("All properties")}><span><Toggle size="xs" checked={tri === "on"} indeterminate={tri === "partial"} onChange={(e) => setProps(allItems, e.currentTarget.checked)} /></span></Tooltip>
        ) : undefined
      }
    >
      {!cls && <div className="empty-hint">{t("Select a class to choose its properties")}</div>}
      {cls && groups.size === 0 && <div className="empty-hint">{t("This class has no properties.")}</div>}
      {cls &&
        [...groups.entries()].map(([ps, cps]) => {
          const items = cps.map((cp) => [ps, cp.Code] as [string, string]);
          const n = items.filter(([a, b]) => checked.has(`${a}|${b}`)).length;
          const st = triOf(n, items.length);
          const isOpen = !open.has(ps); // groups are open by default
          return (
            <div key={ps} className="loin-group">
              <div className="loin-row loin-group-row" onClick={() => toggle(ps)}>
                <Chevron open={isOpen} show onClick={() => toggle(ps)} />
                <span onClick={(e) => e.stopPropagation()}><Toggle size="xs" checked={st === "on"} indeterminate={st === "partial"} onChange={(e) => setProps(items, e.currentTarget.checked)} /></span>
                <span className="loin-name">{ps || t("(no property set)")}</span>
                <Badge size="xs" variant="light" color={n ? "blue" : "gray"}>{n}/{items.length}</Badge>
              </div>
              {isOpen &&
                cps.map((cp) => (
                  <div key={cp.Code} className="loin-row" style={{ paddingLeft: 28 }}>
                    <span className="loin-chevron" />
                    <Toggle size="xs" checked={checked.has(`${ps}|${cp.Code}`)} onChange={(e) => setProps([[ps, cp.Code]], e.currentTarget.checked)} />
                    <span className="loin-name">{cpName(idx, doc.dictionary, cp)}</span>
                    <span className="loin-code">{cp.Code}</span>
                  </div>
                ))}
            </div>
          );
        })}
    </Panel>
  );
}

// ------------------------------------------------------------------ 3. property sets across all classes

interface PsetEntry {
  code: string;
  name: string;
  classes: string[]; // classes owning (pset, code)
}

function PsetPanel({ specKey: key, spec }: { specKey: string; spec?: LoinSpec }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc)!;
  const idx = useProject((s) => s.idx);
  const loin = doc.extras.loin;
  const [filter, setFilter] = useState("");
  const { open, toggle } = useOpenSet();

  // like the desktop pset view: aggregate all classes added to the LOIN
  const groups = useMemo(() => {
    const added = new Set(loin.added_classes ?? []);
    const map = new Map<string, Map<string, PsetEntry>>();
    for (const c of doc.dictionary.Classes ?? []) {
      if (!added.has(c.Code)) continue;
      for (const cp of c.ClassProperties ?? []) {
        const ps = cp.PropertySet ?? "";
        if (!map.has(ps)) map.set(ps, new Map());
        const g = map.get(ps)!;
        if (!g.has(cp.Code)) g.set(cp.Code, { code: cp.Code, name: cpName(idx, doc.dictionary, cp), classes: [] });
        g.get(cp.Code)!.classes.push(c.Code);
      }
    }
    return [...map.entries()].sort(([a], [b]) => a.localeCompare(b, undefined, { numeric: true }));
  }, [doc, idx, loin.added_classes]);

  const isChecked = (cls: string, ps: string, code: string) => (spec?.properties?.[cls] ?? []).some(([a, b]) => (a ?? "") === ps && b === code);
  const countEntry = (ps: string, e: PsetEntry) => e.classes.filter((c) => isChecked(c, ps, e.code)).length;
  const set = (items: [string, string][], value: boolean) => attempt(() => op("loin.set_pset_properties_included", { spec: key, items, included: value }));
  const f = filter.trim().toLowerCase();

  return (
    <Panel
      title={t("Property sets")}
      subtitle={t("Across all classes of the LOIN")}
      count={<Badge variant="light">{t("{{n}} sets", { n: groups.length })}</Badge>}
      filter={filter}
      setFilter={setFilter}
    >
      {groups.length === 0 && <div className="empty-hint">{t("Include classes first – their property sets appear here.")}</div>}
      {groups.map(([ps, entries]) => {
        const list = [...entries.values()].filter((e) => !f || ps.toLowerCase().includes(f) || e.name.toLowerCase().includes(f) || e.code.toLowerCase().includes(f));
        if (!list.length) return null;
        const instTotal = list.reduce((n, e) => n + e.classes.length, 0);
        const instOn = list.reduce((n, e) => n + countEntry(ps, e), 0);
        const st = triOf(instOn, instTotal);
        const isOpen = !!f || open.has(ps);
        const nClasses = new Set(list.flatMap((e) => e.classes)).size;
        return (
          <div key={ps} className="loin-group">
            <div className="loin-row loin-group-row" onClick={() => toggle(ps)}>
              <Chevron open={isOpen} show onClick={() => toggle(ps)} />
              <span onClick={(e) => e.stopPropagation()}>
                <Toggle size="xs" checked={st === "on"} indeterminate={st === "partial"} onChange={(e) => set(list.map((x) => [ps, x.code]), e.currentTarget.checked)} />
              </span>
              <span className="loin-name">{ps || t("(no property set)")}</span>
              <Tooltip label={t("{{n}} properties in {{c}} classes", { n: list.length, c: nClasses })}>
                <Badge size="xs" variant="light" color={instOn ? "blue" : "gray"}>{list.length} · {nClasses}</Badge>
              </Tooltip>
            </div>
            {isOpen &&
              list.map((e) => {
                const n = countEntry(ps, e);
                const est = triOf(n, e.classes.length);
                return (
                  <div key={e.code} className="loin-row" style={{ paddingLeft: 28 }}>
                    <span className="loin-chevron" />
                    <Toggle size="xs" checked={est === "on"} indeterminate={est === "partial"} onChange={(ev) => set([[ps, e.code]], ev.currentTarget.checked)} />
                    <span className="loin-name">{e.name}</span>
                    <span className="loin-code">{e.code}</span>
                    <Tooltip label={e.classes.map((c) => idx.classes.get(c)?.Name ?? c).join(", ")} multiline w={260}>
                      <Badge size="xs" variant="outline" color={n ? "blue" : "gray"}>{n}/{e.classes.length}</Badge>
                    </Tooltip>
                  </div>
                );
              })}
          </div>
        );
      })}
    </Panel>
  );
}

function Wrap({ inline, close, title, children }: { inline?: boolean; close: () => void; title: string; children: React.ReactNode }) {
  if (inline) return <div style={{ height: "100%", display: "flex", flexDirection: "column", minHeight: 0 }}>{children}</div>;
  return (
    <Modal opened onClose={close} title={title} size="95%" styles={{ body: { height: "80vh", display: "flex", flexDirection: "column" } }}>
      {children}
    </Modal>
  );
}

function EntryList({ kind, title, items }: { kind: "purpose" | "milestone"; title: string; items: LoinEntry[] }) {
  const { t } = useTranslation();
  const add = async () => {
    const name = await askText(title, t("Name"));
    if (name) await attempt(() => op(kind === "purpose" ? "loin.add_purpose" : "loin.add_milestone", { name }));
  };
  const move = (i: number, dir: -1 | 1) => {
    const order = items.map((x) => x.guid);
    const j = i + dir;
    if (j < 0 || j >= order.length) return;
    [order[i], order[j]] = [order[j], order[i]];
    void attempt(() => op("loin.reorder", { kind, order }));
  };
  return (
    <Stack gap={4}>
      <Group justify="space-between"><Text fw={600}>{title}</Text><ActionIcon variant="light" onClick={add}><IconPlus size={16} /></ActionIcon></Group>
      {items.map((x, i) => (
        <Group key={x.guid} gap={4} wrap="nowrap">
          <Text size="sm" style={{ flex: 1 }} truncate>{x.name}</Text>
          {kind === "milestone" && (
            <TextInput type="date" size="xs" value={(x.date ?? "").slice(0, 10)} onChange={(e) => attempt(() => op("loin.set_milestone_date", { guid: x.guid, date: e.currentTarget.value ? `${e.currentTarget.value}T00:00:00` : null }))} w={150} />
          )}
          <ActionIcon size="sm" variant="subtle" onClick={() => move(i, -1)} disabled={i === 0}><IconArrowUp size={14} /></ActionIcon>
          <ActionIcon size="sm" variant="subtle" onClick={() => move(i, 1)} disabled={i === items.length - 1}><IconArrowDown size={14} /></ActionIcon>
          <Tooltip label={t("Rename")}>
            <ActionIcon size="sm" variant="subtle" onClick={async () => { const n = await askText(t("Rename"), t("Name"), x.name); if (n) await attempt(() => op("loin.rename", { kind, guid: x.guid, name: n })); }}><IconPencil size={14} /></ActionIcon>
          </Tooltip>
          <ActionIcon size="sm" variant="subtle" color="red" disabled={items.length <= 1} onClick={async () => { if (await askConfirm(t("Delete"), t("Delete '{{name}}' and its specifications?", { name: x.name }), t("Delete"), true)) await attempt(() => op("loin.remove", { kind, guid: x.guid })); }}><IconTrash size={14} /></ActionIcon>
        </Group>
      ))}
    </Stack>
  );
}

const ACTOR_FIELDS: [keyof LoinActor, string][] = [
  ["role", "Role"],
  ["first_name", "First name"],
  ["middle_name", "Middle name"],
  ["last_name", "Last name"],
  ["affiliation", "Affiliation"],
  ["email_address", "E-mail"],
];

function ActorForm({ which, title, actor }: { which: "providing" | "receiving"; title: string; actor?: LoinActor | null }) {
  const { t } = useTranslation();
  const [form, setForm] = useState<LoinActor>(actor ?? {});
  useEffect(() => setForm(actor ?? {}), [actor]);
  return (
    <Stack gap={4} mt="md">
      <Text fw={600}>{title}</Text>
      <Grid gutter={6}>
        {ACTOR_FIELDS.map(([k, label]) => (
          <Grid.Col span={6} key={k}>
            <TextInput label={t(label)} value={(form[k] as string) ?? ""} onChange={(e) => setForm({ ...form, [k]: e.currentTarget.value })} required={k === "role"} />
          </Grid.Col>
        ))}
      </Grid>
      <Group justify="flex-end">
        <Button variant="light" disabled={!form.role} onClick={() => attempt(() => op("loin.set_actor", { which, data: form }), t("Saved"))}>{t("Save")}</Button>
      </Group>
    </Stack>
  );
}
