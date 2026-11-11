import { ActionIcon, Anchor, Badge, Breadcrumbs, Button, Group, Menu, Stack, Tabs, Text, ThemeIcon, Title, Tooltip } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { IconArrowLeft, IconBinaryTree2, IconBox, IconDots, IconLink, IconPencil, IconPlus, IconStack2, IconTrash } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import type { BsddClass } from "../../types";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";
import { ClassPropertyTable } from "../../components/ClassPropertyTable";
import { ClassTree } from "../../components/ClassTree";
import { askDeleteClasses } from "../../components/dialogs";
import { PsetList } from "../../components/PsetList";
import { ClassForm } from "../../forms/ClassForm";
import { Split } from "../../layout/Split";
import { GOP, MATERIAL, MODE_CLASS_TYPE, ancestors, classMode, descendants, gopPropertyUsage, type ClassMode } from "../../model";
import { attempt, notifyOk } from "../../notify";
import { MODE_SECTION, go, openClass } from "../../state/nav";
import { op, useProject } from "../../state/project";
import { openUi } from "../../state/ui";
import { editClassPopup, useClicks } from "../../components/popupEdit";
import { onNavigationCancelled } from "../../components/UnsavedGuard";

export function ClassesPage({ mode }: { mode: ClassMode }) {
  const { code: rawCode } = useParams();
  const code = rawCode ? decodeURIComponent(rawCode) : null;
  const section = MODE_SECTION[mode];
  const codeRef = useRef(code);
  codeRef.current = code;

  // URL → store (deep links, back/forward)
  useEffect(() => {
    if (code && useProject.getState().activeClass !== code) {
      useProject.getState().setActiveClass(code);
      openUi({ revealClass: { code, at: Date.now() } });
    }
  }, [code]);
  // the user chose to stay on a page with unsaved edits: put the tree selection back
  useEffect(
    () =>
      onNavigationCancelled(() => {
        if (codeRef.current && useProject.getState().activeClass !== codeRef.current) {
          useProject.getState().setActiveClass(codeRef.current);
          openUi({ revealClass: { code: codeRef.current, at: Date.now() } });
        }
      }),
    [],
  );
  // store → URL (tree clicks, newly created classes)
  useEffect(
    () =>
      useProject.subscribe((s, prev) => {
        if (s.activeClass === prev.activeClass || !s.activeClass || s.activeClass === codeRef.current) return;
        const cls = s.idx.classes.get(s.activeClass);
        const target = MODE_SECTION[classMode(cls)];
        go(target, s.activeClass, target === section && !!codeRef.current);
      }),
    [section],
  );

  return (
    <Split storeKey={`bsdd-split-${section}`} side={<ClassTree mode={mode} />} showDetail={!!code}>
      {code ? <ClassDetail key={code} code={code} mode={mode} /> : <EmptyDetail mode={mode} />}
    </Split>
  );
}

function EmptyDetail({ mode }: { mode: ClassMode }) {
  const { t } = useTranslation();
  const gop = mode === "gop";
  if (mode === "material") {
    return (
      <Stack align="center" justify="center" h="100%" gap="sm" p="xl">
        <ThemeIcon size={56} radius="xl" variant="light"><IconBox size={30} /></ThemeIcon>
        <Title order={4}>{t("Materials")}</Title>
        <Text c="dimmed" ta="center" maw={420}>{t("Select a material on the left to see its properties and details, or create a new one.")}</Text>
        <Button data-edit leftSection={<IconPlus size={14} />} onClick={() => openUi({ classEditor: { parentCode: null, classType: MATERIAL } })}>
          {t("New material")}
        </Button>
      </Stack>
    );
  }
  return (
    <Stack align="center" justify="center" h="100%" gap="sm" p="xl">
      <ThemeIcon size={56} radius="xl" variant="light">{gop ? <IconStack2 size={30} /> : <IconBinaryTree2 size={30} />}</ThemeIcon>
      <Title order={4}>{gop ? t("Groups of properties") : t("Classes")}</Title>
      <Text c="dimmed" ta="center" maw={420}>
        {gop
          ? t("Select a group of properties on the left. Groups bundle properties that can be reused in classes as property sets.")
          : t("Select a class on the left to see its properties and details, or create a new one.")}
      </Text>
      <Button data-edit leftSection={<IconPlus size={14} />} onClick={() => openUi({ classEditor: { parentCode: null, classType: gop ? GOP : "Class" } })}>
        {gop ? t("New group of properties") : t("New class")}
      </Button>
    </Stack>
  );
}

// the selected tab is kept while browsing from class to class
const lastTab: Record<string, string> = {};

function ClassDetail({ code, mode }: { code: string; mode: ClassMode }) {
  const { t } = useTranslation();
  const clicks = useClicks();
  const idx = useProject((s) => s.idx);
  const activePset = useProject((s) => s.activePset);
  const [tab, setTab] = useState<string>(lastTab[mode] ?? "properties");
  const changeTab = (v: string | null) => {
    if (!v) return;
    lastTab[mode] = v;
    setTab(v);
  };
  const narrow = useMediaQuery("(max-width: 48em)");
  const cls = idx.classes.get(code);
  const section = MODE_SECTION[mode];
  const childType = MODE_CLASS_TYPE[mode];
  // follow renames done by other users: same name and parent, new code
  const last = useRef<BsddClass | undefined>(cls);
  if (cls) last.current = cls;
  const renamedTo = !cls && last.current
    ? [...idx.classes.values()].find((c) => c.Name === last.current!.Name && (c.ParentClassCode ?? null) === (last.current!.ParentClassCode ?? null))?.Code
    : undefined;
  useEffect(() => {
    if (renamedTo) go(MODE_SECTION[classMode(idx.classes.get(renamedTo))], renamedTo, true);
  }, [renamedTo, idx]);

  if (!cls) {
    return (
      <Stack align="center" justify="center" h="100%" p="xl">
        <Text c="dimmed">{t("The class '{{code}}' does not exist (anymore).", { code })}</Text>
        <Button variant="light" onClick={() => go(section)}>{t("Back")}</Button>
      </Stack>
    );
  }
  const gop = cls.ClassType === GOP;
  const path = ancestors(idx, code).reverse();
  const children = idx.children.get(code) ?? [];
  const nProps = (cls.ClassProperties ?? []).length;
  const nRel = (cls.ClassRelations ?? []).length;

  const remove = async () => {
    const d = useProject.getState().doc?.dictionary;
    const result = await askDeleteClasses([cls.Name], (recursive) =>
      d ? gopPropertyUsage(idx, d, recursive ? [code, ...descendants(idx, code)] : [code]) : { names: [], kept: [], otherClasses: 0 },
    );
    if (!result) return;
    const ok = await attempt(() =>
      op("class.delete", { codes: [code], recursive: result.recursive, delete_properties: result.deleteProperties }).then(() => true),
    );
    if (ok) {
      useProject.getState().setActiveClass(null);
      go(section, cls.ParentClassCode && idx.classes.has(cls.ParentClassCode) ? cls.ParentClassCode : null, true);
    }
  };
  const copyLink = async () => {
    await navigator.clipboard?.writeText(window.location.href);
    notifyOk(t("Link copied"));
  };

  return (
    <div className="detail">
      <div className="detail-header">
        {narrow && (
          <Button variant="subtle" size="compact-sm" leftSection={<IconArrowLeft size={14} />} onClick={() => go(section)} mb={4}>
            {gop ? t("Groups of properties") : mode === "material" ? t("Materials") : t("Classes")}
          </Button>
        )}
        {path.length > 0 && (
          <Breadcrumbs separator="›" mb={2} style={{ flexWrap: "wrap" }}>
            {path.map((p) => (
              <Anchor key={p} size="xs" c="dimmed" onClick={() => openClass(p)}>{idx.classes.get(p)?.Name ?? p}</Anchor>
            ))}
          </Breadcrumbs>
        )}
        <Group justify="space-between" align="flex-start" wrap="nowrap" gap="sm">
          <div style={{ minWidth: 0 }}>
            <Group gap={8} wrap="wrap">
              <Title order={3} style={{ wordBreak: "break-word" }}>{cls.Name}</Title>
              {cls.Status && <Badge variant="light" color={cls.Status === "Active" ? "green" : cls.Status === "Inactive" ? "gray" : "yellow"}>{cls.Status}</Badge>}
              {cls.ClassType && cls.ClassType !== "Class" && <Badge variant="outline" color="gray">{cls.ClassType}</Badge>}
            </Group>
            <Text size="sm" c="dimmed" className="mono">{cls.Code}</Text>
            {cls.Definition && <Text size="sm" mt={4} lineClamp={2} maw={900}>{cls.Definition}</Text>}
            {(cls.RelatedIfcEntityNamesList ?? []).length > 0 && (
              <Group gap={4} mt={6}>
                {cls.RelatedIfcEntityNamesList!.map((e) => <Badge key={e} size="sm" variant="dot" color="green">{e}</Badge>)}
              </Group>
            )}
          </div>
          <Group gap={6} wrap="nowrap">
            {!gop && (
              <Tooltip label={t("New subclass")}>
                <Button data-edit variant="default" leftSection={<IconPlus size={14} />} onClick={() => openUi({ classEditor: { parentCode: code, classType: childType } })} visibleFrom="md">
                  {t("Subclass")}
                </Button>
              </Tooltip>
            )}
            <Menu position="bottom-end" shadow="md">
              <Menu.Target><ActionIcon variant="default" size="lg" aria-label={t("More")}><IconDots size={16} /></ActionIcon></Menu.Target>
              <Menu.Dropdown>
                {!gop && <Menu.Item data-edit leftSection={<IconPlus size={14} />} onClick={() => openUi({ classEditor: { parentCode: code, classType: childType } })}>{t("New subclass")}</Menu.Item>}
                <Menu.Item leftSection={<IconPencil size={14} />} onClick={() => openUi({ classEditor: { code } })}>{t("Edit in dialog")}</Menu.Item>
                <Menu.Item leftSection={<IconLink size={14} />} onClick={copyLink}>{t("Copy link to this class")}</Menu.Item>
                <Menu.Divider />
                <Menu.Item data-edit leftSection={<IconTrash size={14} />} color="red" onClick={remove}>{t("Delete")}</Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </div>

      <Tabs value={gop && tab === "children" ? "properties" : tab} onChange={changeTab} className="detail-tabs" keepMounted>
        <Tabs.List px="md">
          <Tabs.Tab value="properties">{t("Properties")} <Badge size="xs" variant="light" color="gray" ml={4}>{nProps}</Badge></Tabs.Tab>
          <Tabs.Tab value="general">{t("General")}</Tabs.Tab>
          <Tabs.Tab value="details">{t("Details")}</Tabs.Tab>
          <Tabs.Tab value="relations">{t("Relations")} <Badge size="xs" variant="light" color="gray" ml={4}>{nRel}</Badge></Tabs.Tab>
          {!gop && <Tabs.Tab value="children">{t("Subclasses")} <Badge size="xs" variant="light" color="gray" ml={4}>{children.length}</Badge></Tabs.Tab>}
        </Tabs.List>
        <Tabs.Panel value="properties" className="detail-panel fill">
          <div className="card-split">
            {!gop && <div className="card-split-side"><PsetList /></div>}
            <div className="card-split-main"><ClassPropertyTable classCode={code} pset={gop ? null : activePset} /></div>
          </div>
        </Tabs.Panel>
        {(["general", "details", "relations"] as const).map((s) => (
          <Tabs.Panel key={s} value={s} className="detail-panel">
            <div className="form-page">
              <ClassForm code={code} section={s} inline onDone={(c) => c !== code && go(section, c, true)} />
            </div>
          </Tabs.Panel>
        ))}
        {!gop && (
          <Tabs.Panel value="children" className="detail-panel">
            <div className="form-page">
              {children.length === 0 && <Text c="dimmed" size="sm">{t("No subclasses")}</Text>}
              <Stack gap={4}>
                {children.map((c) => (
                  <div key={c.Code} className="list-card" {...clicks(() => openClass(c.Code), () => editClassPopup(c.Code))}>
                    <Text size="sm" fw={500} truncate style={{ flex: 1 }}>{c.Name}</Text>
                    <Text size="xs" c="dimmed" className="mono">{c.Code}</Text>
                    <Badge size="xs" variant="light" color="gray">{(c.ClassProperties ?? []).length}</Badge>
                  </div>
                ))}
              </Stack>
              <Button data-edit mt="md" variant="light" leftSection={<IconPlus size={14} />} onClick={() => openUi({ classEditor: { parentCode: code, classType: childType } })}>{t("New subclass")}</Button>
            </div>
          </Tabs.Panel>
        )}
      </Tabs>
    </div>
  );
}
