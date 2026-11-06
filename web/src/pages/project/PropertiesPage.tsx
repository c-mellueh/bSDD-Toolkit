import { ActionIcon, Badge, Button, Group, Menu, Stack, Tabs, Text, TextInput, ThemeIcon, Title, Tooltip } from "@mantine/core";
import { Toggle } from "../../components/Toggle";
import { useMediaQuery } from "@mantine/hooks";
import { IconArrowLeft, IconClipboard, IconCopy, IconDots, IconLink, IconList, IconPlus, IconSearch, IconSquarePlus, IconTrash } from "@tabler/icons-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { BsddProperty } from "../../types";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { copyProperties, readClip } from "../../clipboard";
import { divider, useContextMenu } from "../../components/ContextMenu";
import { askConfirm } from "../../components/dialogs";
import { useListSelection } from "../../components/useListSelection";
import { PropertyForm, type PropertySection } from "../../forms/PropertyForm";
import { setGraphDrag } from "../../graph/dnd";
import { classId, propId } from "../../graph/model";
import { Split } from "../../layout/Split";
import { internalCode } from "../../model";
import { attempt, notifyOk } from "../../notify";
import { go, openClass } from "../../state/nav";
import { op, useProject } from "../../state/project";
import { openUi } from "../../state/ui";

export function PropertiesPage() {
  const { code: rawCode } = useParams();
  const code = rawCode ? decodeURIComponent(rawCode) : null;
  return (
    <Split storeKey="bsdd-split-properties" side={<PropertyList current={code} />} showDetail={!!code}>
      {code ? <PropertyDetail key={code} code={code} /> : <Empty />}
    </Split>
  );
}

function Empty() {
  const { t } = useTranslation();
  return (
    <Stack align="center" justify="center" h="100%" gap="sm" p="xl">
      <ThemeIcon size={56} radius="xl" variant="light"><IconList size={30} /></ThemeIcon>
      <Title order={4}>{t("Properties")}</Title>
      <Text c="dimmed" ta="center" maw={420}>{t("Properties are defined once and then used in classes. Select a property on the left to edit it.")}</Text>
      <Button data-edit leftSection={<IconPlus size={14} />} onClick={() => openUi({ propertyEditor: { onCreated: (c) => go("properties", c) } })}>{t("New property")}</Button>
    </Stack>
  );
}

function PropertyList({ current }: { current: string | null }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const activeClass = useProject((s) => s.activeClass);
  const activePset = useProject((s) => s.activePset);
  const openMenu = useContextMenu((s) => s.open);
  const [filter, setFilter] = useState("");

  const usage = useMemo(() => {
    const m = new Map<string, number>();
    if (!doc) return m;
    const d = doc.dictionary;
    for (const c of d.Classes ?? [])
      for (const cp of c.ClassProperties ?? []) {
        const code = cp.PropertyCode ?? internalCode(d, cp.PropertyUri, "prop");
        if (code) m.set(code, (m.get(code) ?? 0) + 1);
      }
    return m;
  }, [doc]);

  const props = useMemo(() => {
    const list = [...(doc?.dictionary.Properties ?? [])].sort((a, b) => (a.Name ?? "").localeCompare(b.Name ?? "", undefined, { numeric: true }));
    const f = filter.toLowerCase();
    return f ? list.filter((p) => p.Code.toLowerCase().includes(f) || (p.Name ?? "").toLowerCase().includes(f)) : list;
  }, [doc, filter]);
  const sel = useListSelection(props.map((p) => p.Code));
  if (!doc) return null;

  const chosen = () => (sel.selected.length ? sel.selected : current ? [current] : []);
  const remove = async () => {
    const codes = chosen();
    if (!codes.length) return;
    const ok = await askConfirm(t("Delete properties"), t("Delete {{n}} properties? All class properties using them are removed as well.", { n: codes.length }), t("Delete"), true);
    if (ok && (await attempt(() => op("prop.delete", { codes }).then(() => true))) && current && codes.includes(current)) go("properties", null, true);
  };
  const copy = () => {
    const codes = chosen();
    const list = (doc.dictionary.Properties ?? []).filter((p) => codes.includes(p.Code));
    if (!list.length) return;
    copyProperties(list);
    notifyOk(t("{{n}} properties copied", { n: list.length }));
  };
  const paste = async () => {
    const clip = readClip("bsdd-properties");
    if (clip) await attempt(() => op("prop.paste", { payload: clip }));
  };
  const activeName = activeClass ? doc.dictionary.Classes?.find((c) => c.Code === activeClass)?.Name : null;
  const addToClass = async () => {
    const codes = chosen();
    if (!activeClass || !codes.length) return;
    const n = await attempt(() => op<string[]>("cp.add_properties", { class_code: activeClass, property_codes: codes, pset: activePset ?? undefined }));
    if (n) notifyOk(t("{{n}} class properties created", { n: n.length }));
  };
  const onKeyDown = (e: React.KeyboardEvent) => {
    if ((e.target as HTMLElement).tagName === "INPUT") return;
    const ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && e.key.toLowerCase() === "c") { e.preventDefault(); copy(); }
    else if (ctrl && e.key.toLowerCase() === "v") { e.preventDefault(); void paste(); }
    else if (e.key === "Delete") { e.preventDefault(); void remove(); }
  };

  return (
    <div className="pane">
      <div className="side-header">
        <Group justify="space-between" wrap="nowrap">
          <Text fw={600}>{t("Properties")} <Text span c="dimmed" size="sm">{(doc.dictionary.Properties ?? []).length}</Text></Text>
          <Tooltip label={t("New property")}>
            <ActionIcon data-edit variant="light" onClick={() => openUi({ propertyEditor: { onCreated: (c) => go("properties", c) } })} aria-label={t("New property")}><IconPlus size={16} /></ActionIcon>
          </Tooltip>
        </Group>
        <TextInput mt={8} leftSection={<IconSearch size={14} />} placeholder={t("Filter…")} value={filter} onChange={(e) => setFilter(e.currentTarget.value)} />
      </div>
      <div className="pane-body" tabIndex={-1} onKeyDown={onKeyDown}>
        {props.map((p) => {
          const n = usage.get(p.Code) ?? 0;
          const isSel = p.Code === current || (sel.selected.length > 1 && sel.selected.includes(p.Code));
          return (
            <div
              key={p.Code}
              className={`list-row${isSel ? " selected" : ""}`}
              draggable
              onDragStart={(e) => setGraphDrag(e, (sel.selected.includes(p.Code) ? sel.selected : [p.Code]).map(propId))}
              onClick={(e) => {
                sel.click(p.Code, e);
                if (!e.ctrlKey && !e.metaKey && !e.shiftKey) go("properties", p.Code, !!current);
              }}
              onContextMenu={(e) => {
                sel.ensure(p.Code);
                openMenu(e, [
                  { label: t("New"), icon: <IconPlus size={14} />, onClick: () => openUi({ propertyEditor: { onCreated: (c) => go("properties", c) } }) },
                  { label: activeName ? t("Add to class '{{name}}'", { name: activeName }) : t("Add to active class"), icon: <IconSquarePlus size={14} />, onClick: addToClass, disabled: !activeClass },
                  divider,
                  { label: t("Copy"), icon: <IconCopy size={14} />, shortcut: "Ctrl+C", onClick: copy },
                  { label: t("Paste"), icon: <IconClipboard size={14} />, shortcut: "Ctrl+V", onClick: paste, disabled: !readClip("bsdd-properties") },
                  divider,
                  { label: t("Delete"), icon: <IconTrash size={14} />, color: "red", shortcut: "Del", onClick: remove },
                ]);
              }}
            >
              <div style={{ flex: 1, minWidth: 0 }}>
                <Text size="sm" truncate>{p.Name || p.Code}</Text>
                <Text size="xs" c="dimmed" truncate className="mono">{p.Code}{p.DataType ? ` · ${p.DataType}` : ""}</Text>
              </div>
              <Tooltip label={t("Used in {{n}} classes", { n })}>
                <Badge size="xs" variant="light" color={n ? "blue" : "gray"}>{n}</Badge>
              </Tooltip>
            </div>
          );
        })}
        {props.length === 0 && <div className="empty-hint">{t("No properties")}</div>}
      </div>
    </div>
  );
}

let lastPropTab = "general";

function PropertyDetail({ code }: { code: string }) {
  const { t } = useTranslation();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const narrow = useMediaQuery("(max-width: 48em)");
  const [tab, setTabState] = useState<string | null>(lastPropTab);
  const setTab = (v: string | null) => {
    if (v) lastPropTab = v;
    setTabState(v);
  };
  const p = idx.properties.get(code);
  const last = useRef<BsddProperty | undefined>(p);
  if (p) last.current = p;
  const renamedTo = !p && last.current ? [...idx.properties.values()].find((x) => x.Name === last.current!.Name)?.Code : undefined;
  useEffect(() => {
    if (renamedTo) go("properties", renamedTo, true);
  }, [renamedTo]);

  const usedBy = useMemo(() => {
    if (!doc) return [];
    const d = doc.dictionary;
    return (d.Classes ?? []).filter((c) => (c.ClassProperties ?? []).some((cp) => cp.PropertyCode === code || internalCode(d, cp.PropertyUri, "prop") === code));
  }, [doc, code]);
  const classSel = useListSelection(usedBy.map((c) => c.Code));

  if (!p) {
    return (
      <Stack align="center" justify="center" h="100%" p="xl">
        <Text c="dimmed">{t("The property '{{code}}' does not exist (anymore).", { code })}</Text>
        <Button variant="light" onClick={() => go("properties")}>{t("Back")}</Button>
      </Stack>
    );
  }
  const removeFromClasses = async () => {
    if (!classSel.selected.length) return;
    const ok = await askConfirm(t("Remove property from classes"), t("Remove '{{name}}' from {{n}} classes?", { name: p.Name, n: classSel.selected.length }), t("Remove"), true);
    if (ok) await attempt(() => op("cp.remove_property_from_classes", { property_code: code, class_codes: classSel.selected }));
  };
  const remove = async () => {
    const ok = await askConfirm(t("Delete properties"), t("Delete {{n}} properties? All class properties using them are removed as well.", { n: 1 }), t("Delete"), true);
    if (ok && (await attempt(() => op("prop.delete", { codes: [code] }).then(() => true)))) go("properties", null, true);
  };
  const copyLink = async () => {
    await navigator.clipboard?.writeText(window.location.href);
    notifyOk(t("Link copied"));
  };
  const sections: [PropertySection, string][] = [
    ["general", t("General")],
    ["values", t("Allowed values")],
    ["details", t("Details")],
    ["relations", t("Relations")],
  ];

  return (
    <div className="detail">
      <div className="detail-header">
        {narrow && <Button variant="subtle" size="compact-sm" leftSection={<IconArrowLeft size={14} />} onClick={() => go("properties")} mb={4}>{t("Properties")}</Button>}
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <div style={{ minWidth: 0 }}>
            <Group gap={8}>
              <Title order={3} style={{ wordBreak: "break-word" }}>{p.Name}</Title>
              {p.DataType && <Badge variant="light">{p.DataType}</Badge>}
              {(p.Units ?? []).slice(0, 3).map((u) => <Badge key={u} variant="outline" color="gray">{u}</Badge>)}
              {p.Status && <Badge variant="light" color={p.Status === "Active" ? "green" : p.Status === "Inactive" ? "gray" : "yellow"}>{p.Status}</Badge>}
            </Group>
            <Text size="sm" c="dimmed" className="mono">{p.Code}</Text>
            {p.Definition && <Text size="sm" mt={4} lineClamp={2} maw={900}>{p.Definition}</Text>}
          </div>
          <Menu position="bottom-end" shadow="md">
            <Menu.Target><ActionIcon variant="default" size="lg" aria-label={t("More")}><IconDots size={16} /></ActionIcon></Menu.Target>
            <Menu.Dropdown>
              <Menu.Item leftSection={<IconLink size={14} />} onClick={copyLink}>{t("Copy link to this property")}</Menu.Item>
              <Menu.Item leftSection={<IconCopy size={14} />} onClick={() => { copyProperties([p]); notifyOk(t("{{n}} properties copied", { n: 1 })); }}>{t("Copy")}</Menu.Item>
              <Menu.Divider />
              <Menu.Item data-edit leftSection={<IconTrash size={14} />} color="red" onClick={remove}>{t("Delete")}</Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Group>
      </div>
      <Tabs value={tab} onChange={setTab} className="detail-tabs" keepMounted>
        <Tabs.List px="md">
          {sections.map(([k, label]) => (
            <Tabs.Tab key={k} value={k}>
              {label}
              {k === "values" && <Badge size="xs" variant="light" color="gray" ml={4}>{(p.AllowedValues ?? []).length}</Badge>}
              {k === "relations" && <Badge size="xs" variant="light" color="gray" ml={4}>{(p.PropertyRelations ?? []).length}</Badge>}
            </Tabs.Tab>
          ))}
          <Tabs.Tab value="usage">{t("Used by")} <Badge size="xs" variant="light" color="gray" ml={4}>{usedBy.length}</Badge></Tabs.Tab>
        </Tabs.List>
        {sections.map(([k]) => (
          <Tabs.Panel key={k} value={k} className="detail-panel">
            <div className="form-page">
              <PropertyForm code={code} section={k} inline onDone={(c) => c !== code && go("properties", c, true)} />
            </div>
          </Tabs.Panel>
        ))}
        <Tabs.Panel value="usage" className="detail-panel">
          <div className="form-page">
            <Group justify="space-between" mb="xs">
              <Text size="sm" c="dimmed">{t("Classes using '{{code}}'", { code })}</Text>
              <Button data-edit size="xs" variant="light" color="red" leftSection={<IconTrash size={14} />} disabled={!classSel.selected.length} onClick={removeFromClasses}>
                {t("Remove from selected classes")}
              </Button>
            </Group>
            {usedBy.length === 0 && <Text c="dimmed" size="sm">{t("This property is not used by any class yet.")}</Text>}
            <Stack gap={4}>
              {usedBy.map((c) => (
                <div
                  key={c.Code}
                  className={`list-card${classSel.selected.includes(c.Code) ? " selected" : ""}`}
                  draggable
                  onDragStart={(e) => setGraphDrag(e, [classId(c.Code)])}
                  onClick={() => openClass(c.Code)}
                >
                  <Toggle size="xs" checked={classSel.selected.includes(c.Code)} onClick={(e) => e.stopPropagation()} onChange={() => classSel.click(c.Code, { ctrlKey: true, metaKey: false, shiftKey: false })} />
                  <Text size="sm" fw={500} truncate style={{ flex: 1 }}>{c.Name}</Text>
                  <Text size="xs" c="dimmed" className="mono">{c.Code}</Text>
                </div>
              ))}
            </Stack>
          </div>
        </Tabs.Panel>
      </Tabs>
    </div>
  );
}
