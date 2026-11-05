import { ActionIcon, Alert, Avatar, Badge, Button, Center, Group, Loader, Menu, Stack, Text, Tooltip } from "@mantine/core";
import {
  IconArrowBackUp,
  IconArrowForwardUp,
  IconBraces,
  IconChartDots3,
  IconCloudDownload,
  IconCopy,
  IconDatabase,
  IconDownload,
  IconFileExport,
  IconFilePlus,
  IconFileUpload,
  IconHome,
  IconList,
  IconListCheck,
  IconSearch,
  IconSettings,
  IconShare,
  IconStack2,
  IconTerminal2,
} from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate, useParams } from "react-router-dom";
import { api, downloadFile } from "../api";
import { ClassEditor } from "../components/ClassEditor";
import { ClassPropertyEditor } from "../components/ClassPropertyEditor";
import { ClassPropertyTable } from "../components/ClassPropertyTable";
import { ClassTree } from "../components/ClassTree";
import { ContextMenuHost } from "../components/ContextMenu";
import { DictionaryEditor } from "../components/DictionaryEditor";
import { DownloadDialog } from "../components/DownloadDialog";
import { ExportDialog } from "../components/ExportDialog";
import { GopWindow } from "../components/GopWindow";
import { GraphView } from "../components/GraphView";
import { LanguageSelect } from "../components/LanguageSelect";
import { LoinEditor } from "../components/LoinEditor";
import { PropertiesWindow } from "../components/PropertiesWindow";
import { PropertyEditor } from "../components/PropertyEditor";
import { PsetList } from "../components/PsetList";
import { SearchDialog } from "../components/SearchDialog";
import { SettingsDialog } from "../components/SettingsDialog";
import { ShareDialog } from "../components/ShareDialog";
import { ShellPanel } from "../components/ShellPanel";
import { attempt, notifyError } from "../notify";
import { connect, disconnect, redo, undo, useProject } from "../state/project";
import { rememberProject, storageGet, storageSet } from "../state/settings";
import { openUi, useUi, type ExportKind } from "../state/ui";

export function ProjectPage() {
  const { projectId } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const status = useProject((s) => s.status);
  const error = useProject((s) => s.error);
  const doc = useProject((s) => s.doc);
  const activeClass = useProject((s) => s.activeClass);
  const activePset = useProject((s) => s.activePset);
  const history = useProject((s) => s.history);
  const users = useProject((s) => s.users);
  const me = useProject((s) => s.me);
  const shell = useUi((s) => s.shell);
  const [downloadOpen, setDownloadOpen] = useState(false);

  useEffect(() => {
    if (!projectId) return;
    connect(projectId);
    return () => disconnect();
  }, [projectId]);

  const d = doc?.dictionary;
  useEffect(() => {
    if (d && projectId) {
      const name = d.DictionaryName || d.DictionaryCode;
      document.title = `${name} – bSDD Toolkit`;
      rememberProject(projectId, name);
    }
  }, [d?.DictionaryName, d?.DictionaryCode, projectId, d]);

  // global shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const ctrl = e.ctrlKey || e.metaKey;
      const target = e.target as HTMLElement;
      const editing = target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable;
      if (ctrl && !editing && e.key.toLowerCase() === "z" && !e.shiftKey) {
        e.preventDefault();
        void attempt(undo);
      } else if (ctrl && !editing && (e.key.toLowerCase() === "y" || (e.key.toLowerCase() === "z" && e.shiftKey))) {
        e.preventDefault();
        void attempt(redo);
      } else if (ctrl && e.altKey && e.key.toLowerCase() === "s") {
        e.preventDefault();
        openUi({ shell: !useUi.getState().shell });
      } else if (ctrl && e.key.toLowerCase() === "s") {
        e.preventDefault();
        void downloadFile(`/api/projects/${projectId}/dictionary.json`, undefined, "GET").catch(notifyError);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [projectId]);

  if (status === "error") {
    return (
      <Center h="100%">
        <Stack align="center">
          <Alert color="red" title={t("Cannot open dictionary")}>{error === "Project not found" ? t("This link does not exist (anymore).") : error}</Alert>
          <Button onClick={() => navigate("/")}>{t("Back to start page")}</Button>
        </Stack>
      </Center>
    );
  }
  if (!doc || !d) {
    return (
      <Center h="100%">
        <Stack align="center">
          <Loader />
          <Text c="dimmed">{t("Connecting…")}</Text>
        </Stack>
      </Center>
    );
  }

  const exp = (kind: ExportKind) => () => openUi({ exportKind: kind });
  const duplicate = async () => {
    const res = await attempt(() => api<{ id: string }>(`/api/projects/${projectId}/duplicate`, { method: "POST" }));
    if (res) window.open(`/p/${res.id}`, "_blank");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <Group gap={4} px="xs" py={4} wrap="nowrap" style={{ borderBottom: "1px solid var(--mantine-color-default-border)" }}>
        <Tooltip label={t("Start page")}>
          <ActionIcon variant="subtle" onClick={() => navigate("/")}><IconHome size={18} /></ActionIcon>
        </Tooltip>
        <Menu position="bottom-start" shadow="md">
          <Menu.Target><Button variant="subtle" color="gray">{t("File")}</Button></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconFilePlus size={14} />} onClick={() => navigate("/")}>{t("New / open…")}</Menu.Item>
            <Menu.Item leftSection={<IconCloudDownload size={14} />} onClick={() => setDownloadOpen(true)}>{t("Download from bSDD")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconDownload size={14} />} rightSection={<Text size="xs" c="dimmed">Ctrl+S</Text>} onClick={() => downloadFile(`/api/projects/${projectId}/dictionary.json`, undefined, "GET").catch(notifyError)}>{t("Save as bSDD JSON")}</Menu.Item>
            <Menu.Item leftSection={<IconFileUpload size={14} />} onClick={() => downloadFile(`/api/projects/${projectId}/project.json`, undefined, "GET").catch(notifyError)}>{t("Save project file (incl. LOIN)")}</Menu.Item>
            <Menu.Item leftSection={<IconCopy size={14} />} onClick={duplicate}>{t("Duplicate dictionary")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Menu position="bottom-start" shadow="md">
          <Menu.Target><Button variant="subtle" color="gray">{t("Edit")}</Button></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconArrowBackUp size={14} />} rightSection={<Text size="xs" c="dimmed">Ctrl+Z</Text>} disabled={!history.undo} onClick={() => attempt(undo)}>{t("Undo")}</Menu.Item>
            <Menu.Item leftSection={<IconArrowForwardUp size={14} />} rightSection={<Text size="xs" c="dimmed">Ctrl+Y</Text>} disabled={!history.redo} onClick={() => attempt(redo)}>{t("Redo")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconSearch size={14} />} onClick={() => openUi({ search: { kind: "class", onPick: (code) => { useProject.getState().setActiveClass(code); openUi({ revealClass: { code, at: Date.now() } }); } } })}>{t("Search class")}</Menu.Item>
            <Menu.Item leftSection={<IconTerminal2 size={14} />} rightSection={<Text size="xs" c="dimmed">Ctrl+Alt+S</Text>} onClick={() => openUi({ shell: !shell })}>{t("Python shell")}</Menu.Item>
            <Menu.Item leftSection={<IconSettings size={14} />} onClick={() => openUi({ settings: true })}>{t("Settings")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Menu position="bottom-start" shadow="md">
          <Menu.Target><Button variant="subtle" color="gray">{t("Data")}</Button></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconDatabase size={14} />} onClick={() => openUi({ dictionaryEditor: true })}>{t("Dictionary data")}</Menu.Item>
            <Menu.Item leftSection={<IconList size={14} />} onClick={() => openUi({ propertiesWindow: true })}>{t("Properties")}</Menu.Item>
            <Menu.Item leftSection={<IconStack2 size={14} />} onClick={() => openUi({ gopWindow: true })}>{t("Groups of properties")}</Menu.Item>
            <Menu.Item leftSection={<IconListCheck size={14} />} onClick={() => openUi({ loin: true })}>{t("Level of Information Need")}</Menu.Item>
            <Menu.Item leftSection={<IconChartDots3 size={14} />} onClick={() => openUi({ graph: true })}>{t("Graph viewer")}</Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Menu position="bottom-start" shadow="md">
          <Menu.Target><Button variant="subtle" color="gray">{t("Export")}</Button></Menu.Target>
          <Menu.Dropdown>
            <Menu.Item leftSection={<IconFileExport size={14} />} onClick={exp("excel")}>Excel</Menu.Item>
            <Menu.Item leftSection={<IconFileExport size={14} />} onClick={exp("ids")}>IDS</Menu.Item>
            <Menu.Item leftSection={<IconFileExport size={14} />} onClick={exp("iso23386")}>ISO 23386</Menu.Item>
            <Menu.Item leftSection={<IconFileExport size={14} />} onClick={exp("iso7817")}>ISO 7817-3 (LOIN)</Menu.Item>
            <Menu.Item leftSection={<IconFileExport size={14} />} onClick={exp("revit-psets")}>{t("Revit property sets")}</Menu.Item>
            <Menu.Item leftSection={<IconFileExport size={14} />} onClick={exp("revit-shared")}>{t("Revit shared parameters")}</Menu.Item>
            <Menu.Divider />
            <Menu.Item leftSection={<IconBraces size={14} />} onClick={() => downloadFile(`/api/projects/${projectId}/dictionary.json`, undefined, "GET").catch(notifyError)}>bSDD JSON</Menu.Item>
          </Menu.Dropdown>
        </Menu>
        <Tooltip label={`${t("Undo")}${history.undo ? `: ${history.undo}` : ""}`}>
          <ActionIcon variant="subtle" disabled={!history.undo} onClick={() => attempt(undo)}><IconArrowBackUp size={18} /></ActionIcon>
        </Tooltip>
        <Tooltip label={`${t("Redo")}${history.redo ? `: ${history.redo}` : ""}`}>
          <ActionIcon variant="subtle" disabled={!history.redo} onClick={() => attempt(redo)}><IconArrowForwardUp size={18} /></ActionIcon>
        </Tooltip>
        <Text fw={600} size="sm" truncate style={{ flex: 1, textAlign: "center", cursor: "pointer" }} onClick={() => openUi({ dictionaryEditor: true })}>
          {d.DictionaryName || d.DictionaryCode}
        </Text>
        {status !== "online" && <Badge color="orange" variant="light">{t("Reconnecting…")}</Badge>}
        <Avatar.Group spacing="xs">
          {users.slice(0, 6).map((u) => (
            <Tooltip key={u.id} label={u.id === me?.id ? `${u.name} (${t("you")})` : u.name}>
              <Avatar size="sm" color={u.color} radius="xl" style={{ border: `2px solid ${u.color}` }}>{u.name.slice(0, 2).toUpperCase()}</Avatar>
            </Tooltip>
          ))}
          {users.length > 6 && <Avatar size="sm" radius="xl">+{users.length - 6}</Avatar>}
        </Avatar.Group>
        <Button leftSection={<IconShare size={14} />} variant="light" onClick={() => openUi({ share: true })}>{t("Share")}</Button>
        <LanguageSelect />
        <Tooltip label={t("Settings")}><ActionIcon variant="subtle" onClick={() => openUi({ settings: true })}><IconSettings size={18} /></ActionIcon></Tooltip>
      </Group>

      <div style={{ flex: 1, minHeight: 0, display: "flex", flexDirection: "column" }}>
        <Panes
          left={<ClassTree />}
          middle={<PsetList />}
          right={<ClassPropertyTable classCode={activeClass} pset={activePset} />}
        />
        {shell && <ShellPanel />}
      </div>

      <Group gap="md" px="xs" py={2} style={{ borderTop: "1px solid var(--mantine-color-default-border)", fontSize: 12 }}>
        <Text size="xs" c="dimmed">{d.OrganizationCode} | {d.DictionaryCode} | {d.DictionaryName ?? ""} | {d.DictionaryVersion}</Text>
        <Text size="xs" c="dimmed">{(d.Classes ?? []).length} {t("classes")} · {(d.Properties ?? []).length} {t("properties")}</Text>
        <div style={{ flex: 1 }} />
        <RemoteActivity />
      </Group>

      <ContextMenuHost />
      <ClassEditor />
      <ClassPropertyEditor />
      <PropertyEditor />
      <DictionaryEditor />
      <PropertiesWindow />
      <GopWindow />
      <LoinEditor />
      <ExportDialog />
      <SearchDialog />
      <GraphView />
      <SettingsDialog />
      <ShareDialog />
      <DownloadDialog opened={downloadOpen} onClose={() => setDownloadOpen(false)} />
    </div>
  );
}

function RemoteActivity() {
  const { t } = useTranslation();
  const last = useProject((s) => s.lastRemote);
  const users = useProject((s) => s.users);
  const [, force] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => force((x) => x + 1), 5000);
    return () => window.clearInterval(id);
  }, []);
  if (!last || Date.now() - last.at > 15000) return null;
  const user = users.find((u) => u.id === last.author);
  return <Text size="xs" c="dimmed">{t("{{name}} changed the dictionary", { name: user?.name ?? t("Someone") })}</Text>;
}

function Panes({ left, middle, right }: { left: React.ReactNode; middle: React.ReactNode; right: React.ReactNode }) {
  const [widths, setWidths] = useState<[number, number]>(() => storageGet("bsdd-pane-widths", [380, 220]));
  const drag = useRef<{ which: 0 | 1; start: number; initial: [number, number] } | null>(null);
  useEffect(() => {
    const move = (e: MouseEvent) => {
      if (!drag.current) return;
      const delta = e.clientX - drag.current.start;
      const next: [number, number] = [...drag.current.initial];
      next[drag.current.which] = Math.max(160, Math.min(900, drag.current.initial[drag.current.which] + delta));
      setWidths(next);
    };
    const up = () => {
      if (drag.current) storageSet("bsdd-pane-widths", widths);
      drag.current = null;
      document.body.style.cursor = "";
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
    };
  }, [widths]);
  const start = (which: 0 | 1) => (e: React.MouseEvent) => {
    drag.current = { which, start: e.clientX, initial: widths };
    document.body.style.cursor = "col-resize";
    e.preventDefault();
  };
  return (
    <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
      <div style={{ width: widths[0], flex: "none", minWidth: 0 }}>{left}</div>
      <div className="splitter" onMouseDown={start(0)} />
      <div style={{ width: widths[1], flex: "none", minWidth: 0 }}>{middle}</div>
      <div className="splitter" onMouseDown={start(1)} />
      <div style={{ flex: 1, minWidth: 0 }}>{right}</div>
    </div>
  );
}
