/* eslint-disable @typescript-eslint/no-explicit-any */
import { ActionIcon, Badge, Button, Checkbox, Group, Modal, Paper, SegmentedControl, Select, Stack, Text, TextInput, Tooltip } from "@mantine/core";
import { IconArrowRight, IconFocus2, IconPhoto, IconFileCode } from "@tabler/icons-react";
import cytoscape, { type Core } from "cytoscape";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { saveBlob } from "../api";
import { CLASS_RELATION_TYPES, GOP, PROPERTY_RELATION_TYPES, internalCode, resolveProperty } from "../model";
import { attempt } from "../notify";
import { op, useProject } from "../state/project";
import { openUi, useUi } from "../state/ui";

const COLORS: Record<string, string> = {
  class: "#228be6",
  gop: "#7950f2",
  property: "#12b886",
  ifc: "#fd7e14",
  external: "#868e96",
};

export function GraphView() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.graph);
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const activeClass = useProject((s) => s.activeClass);
  const [container, setContainer] = useState<HTMLDivElement | null>(null);
  const cy = useRef<Core | null>(null);
  const [layout, setLayout] = useState<"cose" | "breadthfirst">("cose");
  const layoutRef = useRef(layout);
  layoutRef.current = layout;
  const [showProps, setShowProps] = useState(false);
  const [showIfc, setShowIfc] = useState(true);
  const [showRelations, setShowRelations] = useState(true);
  const [focus, setFocus] = useState<string | null>(null);
  const [selected, setSelected] = useState<{ id: string; kind: string; label: string; code: string } | null>(null);
  const [edgeSource, setEdgeSource] = useState<{ id: string; kind: string; code: string } | null>(null);
  const [edgeType, setEdgeType] = useState("IsSimilarTo");
  const [filter, setFilter] = useState("");

  const elements = useMemo(() => {
    if (!doc) return [];
    const d = doc.dictionary;
    const els: cytoscape.ElementDefinition[] = [];
    const nodes = new Set<string>();
    let classes = d.Classes ?? [];
    if (focus) {
      // focus: class, its ancestors and descendants
      const keep = new Set<string>([focus]);
      let cur = idx.classes.get(focus)?.ParentClassCode;
      while (cur && !keep.has(cur)) {
        keep.add(cur);
        cur = idx.classes.get(cur)?.ParentClassCode;
      }
      const stack = [focus];
      while (stack.length) {
        const c = stack.pop()!;
        for (const k of idx.children.get(c) ?? []) if (!keep.has(k.Code)) { keep.add(k.Code); stack.push(k.Code); }
      }
      classes = classes.filter((c) => keep.has(c.Code));
    }
    if (filter) classes = classes.filter((c) => c.Name.toLowerCase().includes(filter.toLowerCase()) || c.Code.toLowerCase().includes(filter.toLowerCase()));
    const addNode = (id: string, label: string, kind: string, code: string) => {
      if (nodes.has(id)) return;
      nodes.add(id);
      els.push({ data: { id, label, kind, code, color: COLORS[kind] ?? COLORS.external } });
    };
    for (const c of classes) addNode(`c:${c.Code}`, c.Name, c.ClassType === GOP ? "gop" : "class", c.Code);
    for (const c of classes) {
      if (c.ParentClassCode && nodes.has(`c:${c.ParentClassCode}`)) els.push({ data: { id: `p:${c.Code}`, source: `c:${c.Code}`, target: `c:${c.ParentClassCode}`, label: "", kind: "parent" } });
      if (showRelations)
        (c.ClassRelations ?? []).forEach((r, i) => {
          const code = internalCode(d, r.RelatedClassUri, "class");
          let target = code ? `c:${code}` : `x:${r.RelatedClassUri}`;
          if (!code) {
            const isIfc = r.RelatedClassUri.toLowerCase().includes("/uri/buildingsmart/ifc/");
            if (isIfc && !showIfc) return;
            addNode(target, r.RelatedClassName || r.RelatedClassUri.split("/").pop() || r.RelatedClassUri, isIfc ? "ifc" : "external", r.RelatedClassUri);
          }
          if (!nodes.has(target)) return;
          els.push({ data: { id: `r:${c.Code}:${i}`, source: `c:${c.Code}`, target, label: r.RelationType, kind: "relation", index: i, owner: c.Code } });
        });
      if (showIfc)
        for (const ifc of c.RelatedIfcEntityNamesList ?? []) {
          addNode(`ifc:${ifc}`, ifc, "ifc", ifc);
          els.push({ data: { id: `i:${c.Code}:${ifc}`, source: `c:${c.Code}`, target: `ifc:${ifc}`, label: "", kind: "ifc" } });
        }
      if (showProps)
        for (const cp of c.ClassProperties ?? []) {
          const p = resolveProperty(idx, d, cp);
          const id = p ? `pr:${p.Code}` : `x:${cp.PropertyUri}`;
          addNode(id, p?.Name ?? cp.Code, p ? "property" : "external", p?.Code ?? cp.PropertyUri ?? cp.Code);
          els.push({ data: { id: `cp:${c.Code}:${cp.Code}`, source: `c:${c.Code}`, target: id, label: cp.PropertySet ?? "", kind: "usage" } });
        }
    }
    if (showProps && showRelations)
      for (const p of d.Properties ?? []) {
        if (!nodes.has(`pr:${p.Code}`)) continue;
        (p.PropertyRelations ?? []).forEach((r, i) => {
          const code = internalCode(d, r.RelatedPropertyUri, "prop");
          if (code && nodes.has(`pr:${code}`)) els.push({ data: { id: `pr:${p.Code}:${i}`, source: `pr:${p.Code}`, target: `pr:${code}`, label: r.RelationType, kind: "relation", index: i, owner: p.Code, ownerKind: "property" } });
        });
      }
    return els;
  }, [doc, idx, showProps, showIfc, showRelations, focus, filter]);

  useEffect(() => {
    if (!opened || !container) return;
    const instance = cytoscape({
      container,
      elements,
      wheelSensitivity: 0.3,
      maxZoom: 2,
      minZoom: 0.05,
      style: [
        { selector: "node", style: { label: "data(label)", "background-color": "data(color)", color: "#555", "font-size": 10, "text-valign": "bottom", "text-margin-y": 4, width: 18, height: 18 } },
        { selector: "node[kind='property']", style: { shape: "round-rectangle", width: 14, height: 14 } },
        { selector: "node[kind='ifc']", style: { shape: "diamond" } },
        { selector: "node:selected", style: { "border-width": 3, "border-color": "#fab005" } },
        { selector: "edge", style: { width: 1.5, "line-color": "#adb5bd", "target-arrow-color": "#adb5bd", "target-arrow-shape": "triangle", "curve-style": "bezier", label: "data(label)", "font-size": 8, color: "#868e96", "text-rotation": "autorotate" } },
        { selector: "edge[kind='parent']", style: { "line-color": "#74c0fc", "target-arrow-color": "#74c0fc" } },
        { selector: "edge[kind='relation']", style: { "line-style": "dashed", "line-color": "#e599f7", "target-arrow-color": "#e599f7" } },
        { selector: "edge[kind='usage']", style: { "line-color": "#96f2d7", "target-arrow-shape": "none" } },
      ],
      layout: layoutOptions(layout),
    });
    instance.on("tap", "node", (e) => {
      const n = e.target.data();
      setSelected({ id: n.id, kind: n.kind, label: n.label, code: n.code });
    });
    instance.on("tap", (e) => {
      if (e.target === instance) setSelected(null);
    });
    instance.on("dbltap", "node", (e) => {
      const n = e.target.data();
      if (n.kind === "class" || n.kind === "gop") openUi({ classEditor: { code: n.code } });
      if (n.kind === "property") openUi({ propertyEditor: { code: n.code } });
    });
    cy.current = instance;
    // the modal animates in: lay out again once the container has its final size
    const relayout = () => {
      instance.resize();
      instance.layout(layoutOptions(layoutRef.current)).run();
      instance.fit(undefined, 30);
    };
    const timer = window.setTimeout(relayout, 300);
    const observer = new ResizeObserver(() => instance.resize());
    observer.observe(container);
    return () => {
      window.clearTimeout(timer);
      observer.disconnect();
      instance.destroy();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [opened, elements, container]);

  useEffect(() => {
    cy.current?.layout(layoutOptions(layout)).run();
    cy.current?.fit(undefined, 30);
  }, [layout]);

  if (!opened || !doc) return null;

  const connect = async () => {
    if (!edgeSource || !selected) return;
    const kindOk = (k: string) => (k === "class" || k === "gop" ? "class" : k === "property" ? "property" : null);
    const a = kindOk(edgeSource.kind);
    const b = kindOk(selected.kind);
    if (!a || a !== b) return;
    await attempt(() => op("relation.add", { kind: a, code: edgeSource.code, relation: a === "class" ? { RelationType: edgeType, RelatedClassUri: selected.code } : { RelationType: edgeType, RelatedPropertyUri: selected.code } }));
    setEdgeSource(null);
  };

  const exportPng = () => {
    const blob = cy.current?.png({ output: "blob", full: true, scale: 2, bg: "#ffffff" }) as Blob | undefined;
    if (blob) saveBlob(blob, `${doc.dictionary.DictionaryCode}_graph.png`);
  };
  const exportHtml = () => {
    const json = JSON.stringify((cy.current?.json() as any)?.elements ?? {});
    const html = `<!doctype html><html><head><meta charset="utf-8"><title>${doc.dictionary.DictionaryName ?? "bSDD"} graph</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3.31.2/dist/cytoscape.min.js"></script>
<style>html,body,#cy{margin:0;height:100%;font-family:sans-serif}</style></head><body><div id="cy"></div><script>
cytoscape({container:document.getElementById('cy'),elements:${json},layout:{name:'preset'},style:[
{selector:'node',style:{label:'data(label)','background-color':'data(color)','font-size':10,'text-valign':'bottom',width:18,height:18}},
{selector:'edge',style:{width:1.5,'line-color':'#adb5bd','target-arrow-shape':'triangle','target-arrow-color':'#adb5bd','curve-style':'bezier',label:'data(label)','font-size':8}}]});
</script></body></html>`;
    saveBlob(new Blob([html], { type: "text/html" }), `${doc.dictionary.DictionaryCode}_graph.html`);
  };

  const sameKind = edgeSource && selected && ((edgeSource.kind === "property") === (selected.kind === "property")) && ["class", "gop", "property"].includes(selected.kind) && selected.id !== edgeSource.id;

  return (
    <Modal opened onClose={() => useUi.getState().set({ graph: false })} title={t("Graph viewer")} size="100%" styles={{ body: { height: "85vh", display: "flex", flexDirection: "column" } }}>
      <Group gap="sm" mb="xs">
        <SegmentedControl size="xs" value={layout} onChange={(v) => setLayout(v as "cose" | "breadthfirst")} data={[{ value: "cose", label: t("Force") }, { value: "breadthfirst", label: t("Tree") }]} />
        <Checkbox label={t("Properties")} checked={showProps} onChange={(e) => setShowProps(e.currentTarget.checked)} />
        <Checkbox label={t("IFC references")} checked={showIfc} onChange={(e) => setShowIfc(e.currentTarget.checked)} />
        <Checkbox label={t("Relations")} checked={showRelations} onChange={(e) => setShowRelations(e.currentTarget.checked)} />
        <TextInput size="xs" placeholder={t("Filter classes…")} value={filter} onChange={(e) => setFilter(e.currentTarget.value)} w={180} />
        <Tooltip label={t("Show only the active class with its parents and children")}>
          <Button size="xs" variant={focus ? "filled" : "default"} leftSection={<IconFocus2 size={14} />} onClick={() => setFocus(focus ? null : activeClass)} disabled={!focus && !activeClass}>{focus ? t("Show all") : t("Focus active class")}</Button>
        </Tooltip>
        <div style={{ flex: 1 }} />
        <Badge variant="light">{elements.filter((e) => !e.data.source).length} {t("nodes")}</Badge>
        <Tooltip label="PNG"><ActionIcon variant="default" onClick={exportPng}><IconPhoto size={16} /></ActionIcon></Tooltip>
        <Tooltip label="HTML"><ActionIcon variant="default" onClick={exportHtml}><IconFileCode size={16} /></ActionIcon></Tooltip>
      </Group>
      <div style={{ flex: 1, position: "relative", border: "1px solid var(--mantine-color-default-border)", minHeight: 0 }}>
        <div ref={setContainer} style={{ position: "absolute", inset: 0 }} />
        {selected && (
          <Paper shadow="md" p="sm" withBorder style={{ position: "absolute", right: 8, top: 8, width: 300 }}>
            <Stack gap={6}>
              <Text fw={600} size="sm">{selected.label}</Text>
              <Text size="xs" c="dimmed">{selected.kind} · {selected.code}</Text>
              {(selected.kind === "class" || selected.kind === "gop" || selected.kind === "property") && (
                <Group gap={4}>
                  <Button size="xs" variant="light" onClick={() => (selected.kind === "property" ? openUi({ propertyEditor: { code: selected.code } }) : openUi({ classEditor: { code: selected.code } }))}>{t("Edit")}</Button>
                  {selected.kind !== "property" && <Button size="xs" variant="light" onClick={() => { useProject.getState().setActiveClass(selected.code); openUi({ revealClass: { code: selected.code, at: Date.now() } }); }}>{t("Select in tree")}</Button>}
                  <Button size="xs" variant="light" leftSection={<IconArrowRight size={12} />} onClick={() => setEdgeSource({ id: selected.id, kind: selected.kind, code: selected.code })}>{t("Start relation")}</Button>
                </Group>
              )}
              {edgeSource && (
                <Stack gap={4}>
                  <Text size="xs">{t("Relation from '{{code}}' to the selected node", { code: edgeSource.code })}</Text>
                  <Group gap={4} wrap="nowrap">
                    <Select size="xs" data={edgeSource.kind === "property" ? PROPERTY_RELATION_TYPES : CLASS_RELATION_TYPES} value={edgeType} onChange={(v) => setEdgeType(v ?? edgeType)} style={{ flex: 1 }} allowDeselect={false} comboboxProps={{ zIndex: 1000 }} />
                    <Button size="xs" onClick={connect} disabled={!sameKind}>{t("Create")}</Button>
                    <Button size="xs" variant="default" onClick={() => setEdgeSource(null)}>{t("Cancel")}</Button>
                  </Group>
                </Stack>
              )}
            </Stack>
          </Paper>
        )}
      </div>
      <Text size="xs" c="dimmed" mt={4}>{t("Double-click a node to edit it. Select a node, click 'Start relation', select the target node and create the relation.")}</Text>
    </Modal>
  );
}

function layoutOptions(name: "cose" | "breadthfirst"): cytoscape.LayoutOptions {
  if (name === "breadthfirst") return { name: "breadthfirst", directed: true, spacingFactor: 1.2, animate: false } as any;
  return { name: "cose", animate: false, nodeRepulsion: () => 8000, idealEdgeLength: () => 60 } as any;
}
