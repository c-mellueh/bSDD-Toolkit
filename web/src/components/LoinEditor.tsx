import { ActionIcon, Button, Checkbox, FileButton, Grid, Group, Modal, ScrollArea, Select, Stack, Switch, Tabs, Text, TextInput, Tooltip } from "@mantine/core";
import { IconArrowDown, IconArrowUp, IconChevronDown, IconChevronRight, IconDownload, IconPencil, IconPlus, IconTrash, IconUpload } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { downloadFile, readFileText } from "../api";
import { GOP, cpName } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { useUi } from "../state/ui";
import type { BsddClass, LoinActor, LoinEntry } from "../types";
import { askConfirm, askText } from "./dialogs";

export const specKey = (p: string, m: string) => `${p}|${m}`;

export function LoinEditor({ inline }: { inline?: boolean } = {}) {
  const { t } = useTranslation();
  const opened = useUi((s) => s.loin) || !!inline;
  const close = () => useUi.getState().set({ loin: false });
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const projectId = useProject((s) => s.projectId);
  const loin = doc?.extras.loin;
  const [purpose, setPurpose] = useState<string | null>(null);
  const [milestone, setMilestone] = useState<string | null>(null);
  const [current, setCurrent] = useState<string | null>(null);
  const [recursive, setRecursive] = useState(true);
  const [open, setOpen] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (opened && loin && !loin.purposes?.length) void op("loin.init");
  }, [opened, loin]);

  const purposes = loin?.purposes ?? [];
  const milestones = loin?.milestones ?? [];
  const p = purposes.find((x) => x.guid === purpose)?.guid ?? purposes[0]?.guid ?? null;
  const m = milestones.find((x) => x.guid === milestone)?.guid ?? milestones[0]?.guid ?? null;
  const key = p && m ? specKey(p, m) : null;
  const spec = key ? loin?.specs?.[key] : undefined;
  const included = useMemo(() => new Set(spec?.classes ?? []), [spec]);

  if (!opened || !doc || !loin) return null;
  const classes = (doc.dictionary.Classes ?? []).filter((c) => c.ClassType !== GOP);

  const toggleClass = (code: string, value: boolean) => key && attempt(() => op("loin.set_class_included", { spec: key, codes: [code], included: value, recursive }));
  const cls = current ? idx.classes.get(current) : undefined;
  const propItems = (spec?.properties?.[current ?? ""] ?? []).map(([ps, c]) => `${ps}|${c}`);
  const propSet = new Set(propItems);
  const toggleProps = (items: [string, string][], value: boolean) =>
    key && current && attempt(() => op("loin.set_properties_included", { spec: key, class_code: current, items, included: value }));

  const renderTree = (parent: string | null, depth: number): React.ReactNode =>
    (parent === null ? classes.filter((c) => !c.ParentClassCode || !idx.classes.has(c.ParentClassCode)) : (idx.children.get(parent) ?? []).filter((c) => c.ClassType !== GOP)).map((c: BsddClass) => {
      const kids = (idx.children.get(c.Code) ?? []).filter((k) => k.ClassType !== GOP);
      const isOpen = open.has(c.Code);
      return (
        <div key={c.Code}>
          <div className={`row${current === c.Code ? " selected" : ""}`} style={{ paddingLeft: depth * 14 }} onClick={() => setCurrent(c.Code)}>
            <span style={{ width: 18, display: "inline-flex", cursor: "pointer" }} onClick={(e) => { e.stopPropagation(); const n = new Set(open); if (isOpen) n.delete(c.Code); else n.add(c.Code); setOpen(n); }}>
              {kids.length ? (isOpen ? <IconChevronDown size={14} /> : <IconChevronRight size={14} />) : null}
            </span>
            <Checkbox size="xs" checked={included.has(c.Code)} onChange={(e) => toggleClass(c.Code, e.currentTarget.checked)} onClick={(e) => e.stopPropagation()} disabled={!key} />
            <span className="cell" style={{ flex: 1 }}>{c.Name}</span>
            <span className="cell" style={{ opacity: 0.6, fontSize: 12 }}>{c.Code}</span>
          </div>
          {isOpen && renderTree(c.Code, depth + 1)}
        </div>
      );
    });

  const psets = new Map<string, [string, string][]>();
  for (const cp of cls?.ClassProperties ?? []) {
    const ps = cp.PropertySet ?? "";
    if (!psets.has(ps)) psets.set(ps, []);
    psets.get(ps)!.push([ps, cp.Code]);
  }

  const importXml = async (file: File | null) => {
    if (!file) return;
    const xml = await readFileText(file);
    const n = await attempt(() => op<number>("loin.import_xml", { xml }));
    if (n !== undefined) notifyOk(t("{{n}} specifications imported", { n }));
  };

  return (
    <Wrap inline={inline} close={close} title={t("Level of Information Need (ISO 7817-3)")}>
      <Tabs defaultValue="selection" style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
        <Tabs.List mb="xs">
          <Tabs.Tab value="selection">{t("Specifications")}</Tabs.Tab>
          <Tabs.Tab value="setup">{t("Purposes, milestones & actors")}</Tabs.Tab>
          <Group gap="xs" ml="auto">
            <FileButton onChange={importXml} accept=".xml,application/xml">
              {(props) => <Button {...props} variant="default" leftSection={<IconUpload size={14} />}>{t("Import XML")}</Button>}
            </FileButton>
            <Button variant="default" leftSection={<IconDownload size={14} />} onClick={() => attempt(() => downloadFile(`/api/projects/${projectId}/export/iso7817`, { specs: null }))}>{t("Export XML")}</Button>
          </Group>
        </Tabs.List>
        <Tabs.Panel value="selection" style={{ flex: 1, minHeight: 0 }}>
          <Group gap="xs" mb="xs" align="flex-end">
            <Select label={t("Purpose")} data={purposes.map((x) => ({ value: x.guid, label: x.name }))} value={p} onChange={setPurpose} allowDeselect={false} w={220} />
            <Select label={t("Milestone")} data={milestones.map((x) => ({ value: x.guid, label: x.name }))} value={m} onChange={setMilestone} allowDeselect={false} w={220} />
            <Switch label={t("Apply to child classes")} checked={recursive} onChange={(e) => setRecursive(e.currentTarget.checked)} mb={6} />
            <Text size="xs" c="dimmed" mb={8}>{t("{{n}} classes included", { n: included.size })}</Text>
          </Group>
          <div style={{ display: "flex", gap: 12, height: "calc(100% - 60px)" }}>
            <ScrollArea style={{ flex: 1, border: "1px solid var(--mantine-color-default-border)" }}>{renderTree(null, 0)}</ScrollArea>
            <ScrollArea style={{ flex: 1, border: "1px solid var(--mantine-color-default-border)" }}>
              {!cls && <div className="empty-hint">{t("Select a class to choose its properties")}</div>}
              {cls && [...psets.entries()].map(([ps, items]) => {
                const all = items.every(([a, b]) => propSet.has(`${a}|${b}`));
                const some = items.some(([a, b]) => propSet.has(`${a}|${b}`));
                return (
                  <div key={ps}>
                    <div className="row" style={{ fontWeight: 600 }}>
                      <Checkbox size="xs" checked={all} indeterminate={some && !all} onChange={(e) => toggleProps(items, e.currentTarget.checked)} mx={6} />
                      <span className="cell">{ps || t("(no property set)")}</span>
                    </div>
                    {items.map(([a, b]) => {
                      const cp = cls.ClassProperties?.find((x) => x.Code === b && (x.PropertySet ?? "") === a);
                      return (
                        <div key={b} className="row" style={{ paddingLeft: 24 }}>
                          <Checkbox size="xs" checked={propSet.has(`${a}|${b}`)} onChange={(e) => toggleProps([[a, b]], e.currentTarget.checked)} mx={6} />
                          <span className="cell" style={{ flex: 1 }}>{cp ? cpName(idx, doc.dictionary, cp) : b}</span>
                          <span className="cell" style={{ opacity: 0.6, fontSize: 12 }}>{b}</span>
                        </div>
                      );
                    })}
                  </div>
                );
              })}
            </ScrollArea>
          </div>
        </Tabs.Panel>
        <Tabs.Panel value="setup" style={{ overflow: "auto", minHeight: 0 }}>
          <Grid>
            <Grid.Col span={6}><EntryList kind="purpose" title={t("Purposes")} items={purposes} /></Grid.Col>
            <Grid.Col span={6}><EntryList kind="milestone" title={t("Milestones")} items={milestones} /></Grid.Col>
            <Grid.Col span={6}><ActorForm which="providing" title={t("Providing actor")} actor={loin.providing_actor} /></Grid.Col>
            <Grid.Col span={6}><ActorForm which="receiving" title={t("Receiving actor")} actor={loin.receiving_actor} /></Grid.Col>
          </Grid>
        </Tabs.Panel>
      </Tabs>
    </Wrap>
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
