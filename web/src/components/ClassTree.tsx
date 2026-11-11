import { ActionIcon, CloseButton, Group, Menu, TextInput, Tooltip } from "@mantine/core";
import { normalize } from "../fuzzy";
import { useSettings } from "../state/settings";
import { useReadOnly } from "../state/readonly";
import { useElementSize } from "@mantine/hooks";
import {
  IconArrowsMaximize,
  IconArrowsMinimize,
  IconChevronDown,
  IconChevronRight,
  IconClipboard,
  IconColumns,
  IconCopy,
  IconEdit,
  IconFolderPlus,
  IconPlus,
  IconSearch,
  IconTrash,
} from "@tabler/icons-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { setGraphDrag } from "../graph/dnd";
import { classId } from "../graph/model";
import { Tree, type NodeApi, type NodeRendererProps, type TreeApi } from "react-arborist";
import { copyClasses, readClip } from "../clipboard";
import { GOP, descendants } from "../model";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { openUi, useUi } from "../state/ui";
import type { BsddClass } from "../types";
import { divider, useContextMenu, type MenuItem } from "./ContextMenu";
import { askDeleteClasses, askText } from "./dialogs";

interface TreeNode {
  id: string;
  name: string;
  cls: BsddClass;
  children?: TreeNode[];
}

export function ClassTree({ mode = "main" }: { mode?: "main" | "gop" }) {
  const { t } = useTranslation();
  const ro = useReadOnly();
  const doc = useProject((s) => s.doc);
  const idx = useProject((s) => s.idx);
  const users = useProject((s) => s.users);
  const me = useProject((s) => s.me);
  const activeClass = useProject((s) => s.activeClass);
  const setActiveClass = useProject((s) => s.setActiveClass);
  const setSelectedClasses = useProject((s) => s.setSelectedClasses);
  const reveal = useUi((s) => s.revealClass);
  const tree = useRef<TreeApi<TreeNode>>();
  const { ref, width, height } = useElementSize();
  const openMenu = useContextMenu((s) => s.open);
  const [filter, setFilter] = useState("");
  const filterRef = useRef<HTMLInputElement>(null);
  const columns = useSettings((s) => s.treeColumns);
  const setSettings = useSettings((s) => s.set);
  const filtering = filter.trim().length > 0;

  const include = (c: BsddClass) => (mode === "gop" ? c.ClassType === GOP : c.ClassType !== GOP);

  const data = useMemo<TreeNode[]>(() => {
    if (!doc) return [];
    const build = (c: BsddClass, seen: Set<string>): TreeNode => {
      seen.add(c.Code);
      const kids = (idx.children.get(c.Code) ?? []).filter((k) => include(k) && !seen.has(k.Code));
      return { id: c.Code, name: c.Name, cls: c, children: kids.length ? kids.map((k) => build(k, seen)) : undefined };
    };
    const seen = new Set<string>();
    const roots = (doc.dictionary.Classes ?? []).filter((c) => include(c) && !(c.ParentClassCode && idx.classes.has(c.ParentClassCode) && include(idx.classes.get(c.ParentClassCode)!)));
    return roots.map((r) => build(r, seen));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [doc, idx, mode]);

  const matchCount = useMemo(() => {
    if (!filtering) return 0;
    const q = normalize(filter.trim());
    let n = 0;
    const walk = (list: TreeNode[]) => list.forEach((x) => { if (normalize(x.name ?? "").includes(q) || normalize(x.id).includes(q)) n++; if (x.children) walk(x.children); });
    walk(data);
    return n;
  }, [data, filter, filtering]);

  const presence = useMemo(() => {
    const map = new Map<string, string[]>();
    for (const u of users) {
      if (u.id === me?.id || !u.selection?.class) continue;
      const list = map.get(u.selection.class) ?? [];
      list.push(u.color);
      map.set(u.selection.class, list);
    }
    return map;
  }, [users, me]);

  // reveal a class requested from search / other windows
  useEffect(() => {
    if (!reveal || !tree.current) return;
    const node = tree.current.get(reveal.code);
    if (!node) return;
    tree.current.openParents(reveal.code);
    tree.current.select(reveal.code);
    tree.current.scrollTo(reveal.code);
  }, [reveal]);

  const selectedCodes = () => {
    const ids = tree.current ? [...tree.current.selectedIds] : [];
    return ids.length ? ids : activeClass ? [activeClass] : [];
  };

  const newClass = (parent: string | null) => openUi({ classEditor: { parentCode: parent, classType: mode === "gop" ? GOP : "Class" } });

  const copy = (withChildren?: boolean) => {
    if (!doc) return;
    const codes = selectedCodes();
    if (!codes.length) return;
    // include subtrees of collapsed nodes (desktop behaviour) unless explicitly requested
    const collapsed = codes.filter((c) => !tree.current?.get(c)?.isOpen);
    const all = new Set(codes);
    for (const c of withChildren ? codes : collapsed) descendants(idx, c).forEach((d) => all.add(d));
    const n = copyClasses(idx, doc, [...all], false);
    notifyOk(t("{{n}} classes copied", { n }));
  };

  const paste = async () => {
    const clip = readClip("bsdd-classes");
    if (!clip) return;
    const parent = activeClass ?? null;
    const created = await attempt(() => op<string[]>("class.paste", { payload: clip, parent_code: parent }));
    if (created?.length) notifyOk(t("{{n}} classes pasted", { n: created.length }));
  };

  const remove = async () => {
    const codes = selectedCodes();
    if (!codes.length) return;
    const names = codes.map((c) => idx.classes.get(c)?.Name ?? c);
    const result = await askDeleteClasses(names);
    if (!result) return;
    await attempt(() => op("class.delete", { codes, recursive: result.recursive }));
    if (codes.includes(activeClass ?? "")) setActiveClass(null);
  };

  const group = async () => {
    const codes = selectedCodes();
    if (!codes.length) return;
    const name = await askText(t("Group classes"), t("Name of the new parent class"));
    if (!name) return;
    const code = await attempt(() => op<string>("class.group", { codes, name }));
    if (code) setActiveClass(code);
  };

  const expandSelection = (open: boolean) => {
    for (const code of selectedCodes()) {
      const node = tree.current?.get(code);
      if (!node) continue;
      const walk = (n: NodeApi<TreeNode>) => {
        if (open) n.open();
        else n.close();
        n.children?.forEach(walk);
      };
      walk(node);
    }
  };

  const search = () => {
    filterRef.current?.focus();
    filterRef.current?.select();
  };

  const menuItems = (): MenuItem[] => [
    { label: t("New class"), icon: <IconPlus size={14} />, shortcut: "Ctrl+N", onClick: () => newClass(activeClass) },
    { label: t("Edit"), icon: <IconEdit size={14} />, onClick: () => activeClass && openUi({ classEditor: { code: activeClass } }), disabled: !activeClass },
    divider,
    { label: t("Copy"), icon: <IconCopy size={14} />, shortcut: "Ctrl+C", onClick: () => copy() },
    { label: t("Copy with children"), onClick: () => copy(true) },
    { label: t("Paste"), icon: <IconClipboard size={14} />, shortcut: "Ctrl+V", onClick: paste, disabled: !readClip("bsdd-classes") },
    divider,
    { label: t("Group"), icon: <IconFolderPlus size={14} />, shortcut: "Ctrl+G", onClick: group },
    { label: t("Expand selection"), shortcut: "Ctrl+E", onClick: () => expandSelection(true) },
    { label: t("Collapse selection"), shortcut: "Ctrl+Alt+E", onClick: () => expandSelection(false) },
    { label: t("Search"), icon: <IconSearch size={14} />, shortcut: "Ctrl+F", onClick: search },
    { label: t("Reset view"), shortcut: "Ctrl+R", onClick: () => tree.current?.closeAll() },
    divider,
    { label: t("Delete"), icon: <IconTrash size={14} />, shortcut: "Del", color: "red", onClick: remove },
  ];

  const onKeyDown = (e: React.KeyboardEvent) => {
    const target = e.target as HTMLElement;
    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA") return;
    const ctrl = e.ctrlKey || e.metaKey;
    const key = e.key.toLowerCase();
    const run = (fn: () => void) => {
      e.preventDefault();
      e.stopPropagation();
      fn();
    };
    if (ctrl && key === "c") run(() => copy());
    else if (ctrl && key === "v") run(paste);
    else if (ctrl && key === "n") run(() => newClass(activeClass));
    else if (ctrl && key === "g") run(group);
    else if (ctrl && e.altKey && key === "e") run(() => expandSelection(false));
    else if (ctrl && key === "e") run(() => expandSelection(true));
    else if (ctrl && key === "f") run(search);
    else if (ctrl && key === "r") run(() => tree.current?.closeAll());
    else if (key === "delete") run(remove);
    else if (key === "enter" && activeClass) run(() => openUi({ classEditor: { code: activeClass } }));
  };

  const Node = ({ node, style, dragHandle }: NodeRendererProps<TreeNode>) => {
    const c = node.data.cls;
    const dots = presence.get(c.Code);
    return (
      <div
        ref={dragHandle}
        style={style}
        className={`row${node.isSelected ? " selected" : ""}${node.willReceiveDrop ? " drop-target" : ""}`}
        onDragStart={(e) => {
          const nodes = node.isSelected ? node.tree.selectedNodes : [node];
          // a collapsed class brings its whole subtree into the graph, an expanded one only itself
          const codes = new Set<string>();
          for (const n of nodes) {
            codes.add(n.id);
            if (!n.isLeaf && !n.isOpen) descendants(idx, n.id).forEach((x) => codes.add(x));
          }
          setGraphDrag(e, [...codes].map(classId));
        }}
        onContextMenu={(e) => {
          if (!node.isSelected) node.select();
          setActiveClass(c.Code);
          openMenu(e, menuItems());
        }}
      >
        <span style={{ width: 18, flex: "none", display: "inline-flex", cursor: "pointer" }} onClick={(e) => { e.stopPropagation(); node.toggle(); }}>
          {node.isLeaf ? null : node.isOpen ? <IconChevronDown size={14} /> : <IconChevronRight size={14} />}
        </span>
        <span className="cell" style={{ flex: 1, paddingLeft: 0 }} title={c.Name}>
          {c.Name}
          {dots?.map((color, i) => <span key={i} className="presence-dot" style={{ background: color }} />)}
        </span>
        {columns.code && <span className="cell" style={{ width: "34%", opacity: 0.8 }} title={c.Code}>{c.Code}</span>}
        {columns.status && <span className="cell" style={{ width: 64, opacity: 0.6, fontSize: 12 }}>{c.Status ?? ""}</span>}
      </div>
    );
  };

  return (
    <div className="pane" style={{ height: "100%" }}>
      <div className="pane-header">
        <span className="pane-title" style={{ flex: 1 }}>{mode === "gop" ? t("Groups of properties") : t("Classes")}</span>
        <Group gap={2}>
          <Menu position="bottom-end" withinPortal closeOnItemClick={false}>
            <Menu.Target>
              <Tooltip label={t("Columns")}><ActionIcon variant="subtle" size="sm" aria-label={t("Columns")}><IconColumns size={16} /></ActionIcon></Tooltip>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Label>{t("Columns")}</Menu.Label>
              {(["code", "status"] as const).map((k) => (
                <Menu.Item key={k} leftSection={<span style={{ width: 14, display: "inline-block" }}>{columns[k] ? "✓" : ""}</span>} onClick={() => setSettings({ treeColumns: { ...columns, [k]: !columns[k] } })}>
                  {k === "code" ? t("Code") : t("Status")}
                </Menu.Item>
              ))}
            </Menu.Dropdown>
          </Menu>
          <Tooltip label={t("Expand all")}><ActionIcon aria-label={t("Expand all")} variant="subtle" size="sm" onClick={() => tree.current?.openAll()}><IconArrowsMaximize size={16} /></ActionIcon></Tooltip>
          <Tooltip label={t("Collapse all")}><ActionIcon aria-label={t("Collapse all")} variant="subtle" size="sm" onClick={() => tree.current?.closeAll()}><IconArrowsMinimize size={16} /></ActionIcon></Tooltip>
          {!ro && <Tooltip label={t("New class") + " (Ctrl+N)"}><ActionIcon aria-label={t("New class") + " (Ctrl+N)"} variant="light" size="sm" onClick={() => newClass(activeClass && idx.classes.get(activeClass) && include(idx.classes.get(activeClass)!) ? activeClass : null)}><IconPlus size={16} /></ActionIcon></Tooltip>}
        </Group>
      </div>
      <div style={{ padding: "6px 8px", borderBottom: "1px solid var(--mantine-color-default-border)" }}>
        <TextInput
          ref={filterRef}
          size="xs"
          leftSection={<IconSearch size={14} />}
          placeholder={t("Filter…") + " (Ctrl+F)"}
          value={filter}
          onChange={(e) => setFilter(e.currentTarget.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") setFilter("");
            if (e.key === "ArrowDown") tree.current?.focus(tree.current?.visibleNodes[0]?.id);
          }}
          rightSection={filter ? <CloseButton size="sm" onClick={() => setFilter("")} aria-label={t("Clear")} /> : null}
        />
      </div>
      <div className="row" style={{ fontSize: 11, fontWeight: 600, color: "var(--mantine-color-dimmed)", borderBottom: "1px solid var(--mantine-color-default-border)" }}>
        <span className="cell" style={{ flex: 1, paddingLeft: 24 }}>{t("Name")}</span>
        {columns.code && <span className="cell" style={{ width: "34%" }}>{t("Code")}</span>}
        {columns.status && <span className="cell" style={{ width: 64 }}>{t("Status")}</span>}
      </div>
      <div
        className="pane-body"
        ref={ref}
        tabIndex={-1}
        onKeyDown={onKeyDown}
        onContextMenu={(e) => {
          if (e.target === e.currentTarget) openMenu(e, [{ label: t("New class"), onClick: () => newClass(null) }, { label: t("Paste"), onClick: paste, disabled: !readClip("bsdd-classes") }]);
        }}
      >
        {data.length === 0 && <div className="empty-hint">{t("No classes yet. Create one with +.")}</div>}
        {filtering && data.length > 0 && !matchCount && <div className="empty-hint">{t("No matching classes")}</div>}
        {width > 0 && height > 0 && (
          <Tree<TreeNode>
            disableDrag={ro}
            disableDrop={ro || filtering}
            searchTerm={filter}
            searchMatch={(node, term) => {
              const q = normalize(term.trim());
              return normalize(node.data.name ?? "").includes(q) || normalize(node.data.id).includes(q);
            }}
            ref={tree}
            data={data}
            width={width}
            height={height}
            rowHeight={26}
            indent={14}
            openByDefault={false}
            disableEdit
            disableMultiSelection={false}
            selection={activeClass ?? undefined}
            selectionFollowsFocus // arrow keys show the class right away
            onActivate={(node) => setActiveClass(node.id)}
            onSelect={(nodes) => {
              setSelectedClasses(nodes.map((n) => n.id));
              if (nodes.length === 1) setActiveClass(nodes[0].id);
            }}
            onMove={async ({ dragIds, parentId, index }) => {
              // arborist's index counts the target's current children (including dragged ones)
              const siblings = (parentId ? idx.children.get(parentId) ?? [] : (doc?.dictionary.Classes ?? []).filter((c) => !c.ParentClassCode || !idx.classes.has(c.ParentClassCode))).filter(include);
              let before: string | null = null;
              for (let i = index; i < siblings.length; i++) {
                if (!dragIds.includes(siblings[i].Code)) {
                  before = siblings[i].Code;
                  break;
                }
              }
              await attempt(() => op("class.move", { codes: dragIds, parent_code: parentId, before_code: before }));
            }}
          >
            {Node}
          </Tree>
        )}
      </div>
    </div>
  );
}
