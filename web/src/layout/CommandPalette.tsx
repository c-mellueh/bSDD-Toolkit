/** Ctrl+K palette: jump to classes, groups, properties, pages and common actions. */
import { Badge, Group, Kbd, Modal, ScrollArea, Text, TextInput } from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";
import {
  IconBinaryTree2,
  IconBolt,
  IconChartDots3,
  IconFileExport,
  IconLayoutDashboard,
  IconList,
  IconListCheck,
  IconPlus,
  IconSearch,
  IconShare,
  IconStack2,
  IconTerminal2,
  IconBox,
} from "@tabler/icons-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { rowScore } from "../fuzzy";
import { GOP, MATERIAL } from "../model";
import { go, openClass, openProperty } from "../state/nav";
import { useProject } from "../state/project";
import { openUi, useUi } from "../state/ui";
import { useReadOnly } from "../state/readonly";

interface Item {
  key: string;
  kind: "action" | "class" | "group" | "property";
  label: string;
  sub?: string;
  cells: string[];
  icon: React.ReactNode;
  run: () => void;
}

const LIMIT = 60;

export function CommandPalette() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.palette);
  const doc = useProject((s) => s.doc);
  const [query, setQuery] = useState("");
  const [debounced] = useDebouncedValue(query, 80);
  const [cursor, setCursor] = useState(0);
  const list = useRef<HTMLDivElement | null>(null);
  const close = () => useUi.getState().set({ palette: false });

  useEffect(() => {
    if (opened) {
      setQuery("");
      setCursor(0);
    }
  }, [opened]);

  const ro = useReadOnly();
  const actions = useMemo<Item[]>(() => {
    const a = (key: string, label: string, icon: React.ReactNode, run: () => void): Item => ({ key, kind: "action", label, cells: [label], icon, run });
    return [
      a("go-overview", t("Overview"), <IconLayoutDashboard size={16} />, () => go("")),
      a("go-classes", t("Classes"), <IconBinaryTree2 size={16} />, () => go("classes")),
      a("go-groups", t("Groups of properties"), <IconStack2 size={16} />, () => go("groups")),
      a("go-materials", t("Materials"), <IconBox size={16} />, () => go("materials")),
      a("go-properties", t("Properties"), <IconList size={16} />, () => go("properties")),
      a("go-loin", t("Level of Information Need"), <IconListCheck size={16} />, () => go("loin")),
      a("go-graph", t("Graph viewer"), <IconChartDots3 size={16} />, () => go("graph")),
      a("go-export", t("Export"), <IconFileExport size={16} />, () => go("export")),
      a("new-class", t("New class"), <IconPlus size={16} />, () => openUi({ classEditor: { parentCode: null, classType: "Class" } })),
      a("new-material", t("New material"), <IconPlus size={16} />, () => openUi({ classEditor: { parentCode: null, classType: MATERIAL } })),
      a("new-property", t("New property"), <IconPlus size={16} />, () => openUi({ propertyEditor: {} })),
      a("shell", t("Python shell"), <IconTerminal2 size={16} />, () => openUi({ shell: !useUi.getState().shell })),
      a("share", t("Share"), <IconShare size={16} />, () => openUi({ share: true })),
    ].filter((x) => !ro || !x.key.startsWith("new-"));
  }, [t, ro]);

  const entities = useMemo<Item[]>(() => {
    if (!doc) return [];
    const out: Item[] = [];
    for (const c of doc.dictionary.Classes ?? []) {
      const gop = c.ClassType === GOP;
      const material = c.ClassType === MATERIAL;
      out.push({
        key: `c:${c.Code}`,
        kind: gop ? "group" : "class",
        label: c.Name || c.Code,
        sub: c.Code,
        cells: [c.Code, c.Name ?? "", c.ClassType ?? "Class"],
        icon: gop ? <IconStack2 size={16} /> : material ? <IconBox size={16} /> : <IconBinaryTree2 size={16} />,
        run: () => openClass(c.Code),
      });
    }
    for (const p of doc.dictionary.Properties ?? []) {
      out.push({ key: `p:${p.Code}`, kind: "property", label: p.Name || p.Code, sub: p.Code, cells: [p.Code, p.Name ?? "", p.DataType ?? ""], icon: <IconList size={16} />, run: () => openProperty(p.Code) });
    }
    return out;
  }, [doc]);

  const results = useMemo(() => {
    const q = debounced.trim();
    if (!q) return actions;
    const scored = [...actions, ...entities]
      .map((it) => ({ it, score: rowScore(q, it.cells, false) + (it.kind === "action" ? -5 : 0) }))
      .filter((r) => r.score > 60)
      .sort((a, b) => b.score - a.score)
      .slice(0, LIMIT);
    return scored.map((r) => r.it);
  }, [debounced, actions, entities]);

  useEffect(() => {
    list.current?.querySelector(`[data-index="${cursor}"]`)?.scrollIntoView({ block: "nearest" });
  }, [cursor]);

  if (!opened) return null;
  const run = (it: Item) => {
    close();
    it.run();
  };
  const kindLabel: Record<Item["kind"], string> = { action: t("Action"), class: t("Class"), group: t("Group of properties"), property: t("Property") };

  return (
    <Modal opened onClose={close} withCloseButton={false} size="lg" padding={0} yOffset="10vh" zIndex={500}>
      <TextInput
        size="md"
        variant="unstyled"
        px="md"
        py={4}
        leftSection={<IconSearch size={18} />}
        placeholder={t("Search classes, properties, pages…")}
        value={query}
        onChange={(e) => { setQuery(e.currentTarget.value); setCursor(0); }}
        data-autofocus
        onKeyDown={(e) => {
          if (e.key === "ArrowDown") { e.preventDefault(); setCursor((c) => Math.min(c + 1, results.length - 1)); }
          else if (e.key === "ArrowUp") { e.preventDefault(); setCursor((c) => Math.max(c - 1, 0)); }
          else if (e.key === "Enter" && results[cursor]) run(results[cursor]);
        }}
        style={{ borderBottom: "1px solid var(--mantine-color-default-border)" }}
      />
      <ScrollArea.Autosize mah="60vh" viewportRef={list}>
        <div style={{ padding: 6 }}>
          {results.length === 0 && <Text c="dimmed" size="sm" p="md" ta="center">{t("Nothing found")}</Text>}
          {results.map((it, i) => (
            <div
              key={it.key}
              data-index={i}
              className={`palette-item${i === cursor ? " active" : ""}`}
              onMouseMove={() => i !== cursor && setCursor(i)}
              onClick={() => run(it)}
            >
              <span className="palette-icon">{it.kind === "action" && debounced ? <IconBolt size={16} /> : it.icon}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <Text size="sm" truncate>{it.label}</Text>
                {it.sub && <Text size="xs" c="dimmed" truncate className="mono">{it.sub}</Text>}
              </div>
              {debounced && <Badge size="xs" variant="light" color={it.kind === "property" ? "blue" : it.kind === "group" ? "violet" : it.kind === "class" ? "orange" : "gray"}>{kindLabel[it.kind]}</Badge>}
            </div>
          ))}
        </div>
      </ScrollArea.Autosize>
      <Group gap="md" px="md" py={6} style={{ borderTop: "1px solid var(--mantine-color-default-border)" }}>
        <Text size="xs" c="dimmed"><Kbd size="xs">↑</Kbd> <Kbd size="xs">↓</Kbd> {t("navigate")}</Text>
        <Text size="xs" c="dimmed"><Kbd size="xs">Enter</Kbd> {t("open")}</Text>
        <Text size="xs" c="dimmed"><Kbd size="xs">Esc</Kbd> {t("close")}</Text>
      </Group>
    </Modal>
  );
}
