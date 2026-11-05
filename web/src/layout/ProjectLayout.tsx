import {
  ActionIcon,
  Alert,
  AppShell,
  Avatar,
  Badge,
  Burger,
  Button,
  Center,
  Divider,
  Group,
  Kbd,
  Loader,
  Menu,
  NavLink,
  ScrollArea,
  Stack,
  Text,
  Tooltip,
  UnstyledButton,
  useComputedColorScheme,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import {
  IconArrowBackUp,
  IconArrowForwardUp,
  IconBinaryTree2,
  IconChartDots3,
  IconChevronsLeft,
  IconChevronsRight,
  IconCloudDownload,
  IconCopy,
  IconDeviceFloppy,
  IconDotsVertical,
  IconDownload,
  IconFileExport,
  IconHome,
  IconLayoutDashboard,
  IconList,
  IconListCheck,
  IconMoon,
  IconSearch,
  IconSettings,
  IconShare,
  IconStack2,
  IconSun,
  IconTerminal2,
} from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Outlet, useLocation, useNavigate, useParams } from "react-router-dom";
import { api, downloadFile } from "../api";
import { ClassEditor } from "../components/ClassEditor";
import { ClassPropertyEditor } from "../components/ClassPropertyEditor";
import { ContextMenuHost } from "../components/ContextMenu";
import { DictionaryEditor } from "../components/DictionaryEditor";
import { DownloadDialog } from "../components/DownloadDialog";
import { ExportDialog } from "../components/ExportDialog";
import { LanguageSelect } from "../components/LanguageSelect";
import { PropertyEditor } from "../components/PropertyEditor";
import { SearchDialog } from "../components/SearchDialog";
import { SettingsDialog } from "../components/SettingsDialog";
import { ShareDialog } from "../components/ShareDialog";
import { ShellPanel } from "../components/ShellPanel";
import { GOP } from "../model";
import { attempt, notifyError } from "../notify";
import { classSection, go, projectPath, setNavigator, type Section } from "../state/nav";
import { connect, disconnect, redo, undo, useProject } from "../state/project";
import { rememberProject, storageGet, storageSet, useSettings } from "../state/settings";
import { openUi, useUi } from "../state/ui";
import { CommandPalette } from "./CommandPalette";

export function ProjectLayout() {
  const { projectId } = useParams();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const status = useProject((s) => s.status);
  const error = useProject((s) => s.error);
  const doc = useProject((s) => s.doc);
  const shell = useUi((s) => s.shell);
  const [mobileOpen, mobile] = useDisclosure(false);
  const [collapsed, setCollapsed] = useState(() => storageGet("bsdd-nav-collapsed", false));
  const [downloadOpen, setDownloadOpen] = useState(false);

  useEffect(() => {
    setNavigator(navigate);
    return () => setNavigator(null);
  }, [navigate]);

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

  // close the mobile navigation after navigating
  useEffect(() => mobile.close(), [location.pathname]); // eslint-disable-line react-hooks/exhaustive-deps

  // requests from components that still use the old window flags → navigate instead
  useEffect(
    () =>
      useUi.subscribe((s, prev) => {
        const map: [keyof typeof s, Section][] = [["graph", "graph"], ["loin", "loin"], ["propertiesWindow", "properties"], ["gopWindow", "groups"]];
        for (const [flag, section] of map) {
          if (s[flag] && !prev[flag]) {
            useUi.getState().set({ [flag]: false });
            go(section);
          }
        }
        if (s.revealClass && s.revealClass !== prev.revealClass) {
          const code = s.revealClass.code;
          const target = projectPath(classSection(code), code);
          if (!window.location.pathname.startsWith(target)) navigate(target);
        }
      }),
    [navigate],
  );

  // global shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const ctrl = e.ctrlKey || e.metaKey;
      const target = e.target as HTMLElement;
      const editing = target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable;
      const k = e.key.toLowerCase();
      if (ctrl && !editing && k === "z" && !e.shiftKey) {
        e.preventDefault();
        void attempt(undo);
      } else if (ctrl && !editing && (k === "y" || (k === "z" && e.shiftKey))) {
        e.preventDefault();
        void attempt(redo);
      } else if (ctrl && k === "k") {
        e.preventDefault();
        openUi({ palette: true });
      } else if (ctrl && e.altKey && k === "s") {
        e.preventDefault();
        openUi({ shell: !useUi.getState().shell });
      } else if (ctrl && k === "s") {
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

  const toggleCollapsed = () => {
    setCollapsed((c) => {
      storageSet("bsdd-nav-collapsed", !c);
      return !c;
    });
  };
  const navWidth = collapsed ? 64 : 236;

  return (
    <AppShell header={{ height: 52 }} navbar={{ width: navWidth, breakpoint: "sm", collapsed: { mobile: !mobileOpen } }} padding={0}>
      <AppShell.Header>
        <Header mobileOpen={mobileOpen} toggleMobile={mobile.toggle} />
      </AppShell.Header>
      <AppShell.Navbar>
        <Navigation collapsed={collapsed} onToggle={toggleCollapsed} onDownload={() => setDownloadOpen(true)} />
      </AppShell.Navbar>
      <AppShell.Main className="app-main">
        <div className="app-content">
          <Outlet />
        </div>
        {shell && <ShellPanel />}
      </AppShell.Main>

      <ContextMenuHost />
      <ClassEditor />
      <ClassPropertyEditor />
      <PropertyEditor />
      <DictionaryEditor />
      <ExportDialog />
      <SearchDialog />
      <SettingsDialog />
      <ShareDialog />
      <CommandPalette />
      <DownloadDialog opened={downloadOpen} onClose={() => setDownloadOpen(false)} />
    </AppShell>
  );
}

// ------------------------------------------------------------------ header

function Header({ mobileOpen, toggleMobile }: { mobileOpen: boolean; toggleMobile: () => void }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const d = useProject((s) => s.doc!.dictionary);
  const status = useProject((s) => s.status);
  const history = useProject((s) => s.history);
  const users = useProject((s) => s.users);
  const me = useProject((s) => s.me);
  const setSettings = useSettings((s) => s.set);
  const scheme = useComputedColorScheme("light");
  const mac = typeof navigator !== "undefined" && /Mac/.test(navigator.platform);

  return (
    <Group h="100%" px="sm" gap="xs" wrap="nowrap">
      <Burger opened={mobileOpen} onClick={toggleMobile} hiddenFrom="sm" size="sm" />
      <UnstyledButton onClick={() => navigate("/")} visibleFrom="xs" aria-label={t("Start page")}>
        <Group gap={8} wrap="nowrap">
          <img src="/favicon.svg" width={26} height={26} alt="" />
          <Text fw={700} visibleFrom="md">bSDD Toolkit</Text>
        </Group>
      </UnstyledButton>
      <Divider orientation="vertical" visibleFrom="md" />
      <UnstyledButton onClick={() => go("")} style={{ minWidth: 0 }}>
        <Group gap={6} wrap="nowrap" style={{ minWidth: 0 }}>
          <Text fw={600} truncate>{d.DictionaryName || d.DictionaryCode}</Text>
          <Badge variant="light" color="gray" visibleFrom="sm" style={{ flex: "none" }}>v{d.DictionaryVersion}</Badge>
        </Group>
      </UnstyledButton>

      <div style={{ flex: 1 }} />

      <UnstyledButton className="search-button" onClick={() => openUi({ palette: true })} visibleFrom="sm">
        <IconSearch size={15} />
        <Text size="sm" c="dimmed" style={{ flex: 1 }}>{t("Search…")}</Text>
        <Kbd size="xs">{mac ? "⌘" : "Ctrl"} K</Kbd>
      </UnstyledButton>
      <ActionIcon variant="subtle" color="gray" hiddenFrom="sm" onClick={() => openUi({ palette: true })} aria-label={t("Search")}><IconSearch size={18} /></ActionIcon>

      <div style={{ flex: 1 }} />

      {status !== "online" && <Badge color="orange" variant="light">{t("Reconnecting…")}</Badge>}
      <Group gap={2} wrap="nowrap">
        <Tooltip label={`${t("Undo")}${history.undo ? `: ${history.undo}` : ""} (Ctrl+Z)`}>
          <ActionIcon variant="subtle" color="gray" disabled={!history.undo} onClick={() => attempt(undo)} aria-label={t("Undo")}><IconArrowBackUp size={18} /></ActionIcon>
        </Tooltip>
        <Tooltip label={`${t("Redo")}${history.redo ? `: ${history.redo}` : ""} (Ctrl+Y)`}>
          <ActionIcon variant="subtle" color="gray" disabled={!history.redo} onClick={() => attempt(redo)} aria-label={t("Redo")}><IconArrowForwardUp size={18} /></ActionIcon>
        </Tooltip>
      </Group>
      <Avatar.Group spacing="xs" visibleFrom="md">
        {users.slice(0, 5).map((u) => (
          <Tooltip key={u.id} label={u.id === me?.id ? `${u.name} (${t("you")})` : u.name}>
            <Avatar size={28} color={u.color} radius="xl" style={{ border: `2px solid ${u.color}` }}>{u.name.slice(0, 2).toUpperCase()}</Avatar>
          </Tooltip>
        ))}
        {users.length > 5 && <Avatar size={28} radius="xl">+{users.length - 5}</Avatar>}
      </Avatar.Group>
      <Button leftSection={<IconShare size={14} />} variant="filled" size="xs" onClick={() => openUi({ share: true })} visibleFrom="xs">{t("Share")}</Button>
      <Group gap={2} wrap="nowrap" visibleFrom="lg">
        <LanguageSelect />
        <Tooltip label={scheme === "dark" ? t("Light") : t("Dark")}>
          <ActionIcon variant="subtle" color="gray" onClick={() => setSettings({ theme: scheme === "dark" ? "light" : "dark" })} aria-label={t("Theme")}>
            {scheme === "dark" ? <IconSun size={18} /> : <IconMoon size={18} />}
          </ActionIcon>
        </Tooltip>
        <Tooltip label={t("Settings")}><ActionIcon variant="subtle" color="gray" onClick={() => openUi({ settings: true })} aria-label={t("Settings")}><IconSettings size={18} /></ActionIcon></Tooltip>
      </Group>
      <Menu position="bottom-end" shadow="md">
        <Menu.Target>
          <ActionIcon variant="subtle" color="gray" hiddenFrom="lg" aria-label={t("More")}><IconDotsVertical size={18} /></ActionIcon>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Item leftSection={<IconShare size={14} />} onClick={() => openUi({ share: true })}>{t("Share")}</Menu.Item>
          <Menu.Item leftSection={scheme === "dark" ? <IconSun size={14} /> : <IconMoon size={14} />} onClick={() => setSettings({ theme: scheme === "dark" ? "light" : "dark" })}>
            {scheme === "dark" ? t("Light") : t("Dark")}
          </Menu.Item>
          <Menu.Item leftSection={<IconSettings size={14} />} onClick={() => openUi({ settings: true })}>{t("Settings")}</Menu.Item>
          <Menu.Divider />
          <div style={{ padding: "4px 8px" }}><LanguageSelect /></div>
        </Menu.Dropdown>
      </Menu>
    </Group>
  );
}

// ------------------------------------------------------------------ navigation

function Navigation({ collapsed, onToggle, onDownload }: { collapsed: boolean; onToggle: () => void; onDownload: () => void }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const projectId = useProject((s) => s.projectId);
  const d = useProject((s) => s.doc!.dictionary);
  const shell = useUi((s) => s.shell);
  const classes = d.Classes ?? [];
  const nGop = classes.filter((c) => c.ClassType === GOP).length;
  const base = `/p/${projectId}`;
  const section = location.pathname.slice(base.length).split("/")[1] ?? "";

  const items: { key: Section; label: string; icon: React.ReactNode; count?: number }[] = [
    { key: "", label: t("Overview"), icon: <IconLayoutDashboard size={18} /> },
    { key: "classes", label: t("Classes"), icon: <IconBinaryTree2 size={18} />, count: classes.length - nGop },
    { key: "groups", label: t("Groups of properties"), icon: <IconStack2 size={18} />, count: nGop },
    { key: "properties", label: t("Properties"), icon: <IconList size={18} />, count: (d.Properties ?? []).length },
    { key: "loin", label: t("Information need (LOIN)"), icon: <IconListCheck size={18} /> },
    { key: "graph", label: t("Graph viewer"), icon: <IconChartDots3 size={18} /> },
    { key: "export", label: t("Export"), icon: <IconFileExport size={18} /> },
  ];

  const download = (path: string) => downloadFile(`/api/projects/${projectId}/${path}`, undefined, "GET").catch(notifyError);
  const duplicate = async () => {
    const res = await attempt(() => api<{ id: string }>(`/api/projects/${projectId}/duplicate`, { method: "POST" }));
    if (res) window.open(`/p/${res.id}`, "_blank");
  };

  const link = (label: string, icon: React.ReactNode, active: boolean, onClick: () => void, count?: number) => {
    const el = (
      <NavLink
        key={label}
        label={collapsed ? undefined : label}
        leftSection={icon}
        rightSection={!collapsed && count !== undefined ? <Badge size="xs" variant="light" color="gray">{count}</Badge> : undefined}
        active={active}
        onClick={onClick}
        className={collapsed ? "nav-collapsed" : undefined}
        aria-label={label}
      />
    );
    return collapsed ? <Tooltip key={label} label={label} position="right">{el}</Tooltip> : el;
  };

  return (
    <Stack h="100%" gap={0}>
      <ScrollArea style={{ flex: 1 }} p={6}>
        {items.map((it) => link(it.label, it.icon, section === it.key, () => navigate(it.key ? `${base}/${it.key}` : base), it.count))}
        <Divider my={6} />
        {link(t("Python shell"), <IconTerminal2 size={18} />, shell, () => openUi({ shell: !shell }))}
      </ScrollArea>
      <Divider />
      <Stack gap={0} p={6}>
        {collapsed ? (
          <Menu position="right-end" shadow="md">
            <Menu.Target>
              <Tooltip label={t("File")} position="right"><NavLink leftSection={<IconDeviceFloppy size={18} />} className="nav-collapsed" aria-label={t("File")} /></Tooltip>
            </Menu.Target>
            <FileMenu download={download} duplicate={duplicate} onDownload={onDownload} />
          </Menu>
        ) : (
          <Menu position="top-start" shadow="md" width={260}>
            <Menu.Target>
              <NavLink label={t("File")} leftSection={<IconDeviceFloppy size={18} />} />
            </Menu.Target>
            <FileMenu download={download} duplicate={duplicate} onDownload={onDownload} />
          </Menu>
        )}
        {link(t("Start page"), <IconHome size={18} />, false, () => navigate("/"))}
        {link(collapsed ? t("Expand sidebar") : t("Collapse sidebar"), collapsed ? <IconChevronsRight size={18} /> : <IconChevronsLeft size={18} />, false, onToggle)}
      </Stack>
    </Stack>
  );
}

function FileMenu({ download, duplicate, onDownload }: { download: (p: string) => void; duplicate: () => void; onDownload: () => void }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  return (
    <Menu.Dropdown>
      <Menu.Item leftSection={<IconDownload size={14} />} rightSection={<Text size="xs" c="dimmed">Ctrl+S</Text>} onClick={() => download("dictionary.json")}>{t("Save as bSDD JSON")}</Menu.Item>
      <Menu.Item leftSection={<IconDownload size={14} />} onClick={() => download("project.json")}>{t("Save project file (incl. LOIN)")}</Menu.Item>
      <Menu.Item leftSection={<IconCopy size={14} />} onClick={duplicate}>{t("Duplicate dictionary")}</Menu.Item>
      <Menu.Divider />
      <Menu.Item leftSection={<IconHome size={14} />} onClick={() => navigate("/")}>{t("New / open…")}</Menu.Item>
      <Menu.Item leftSection={<IconCloudDownload size={14} />} onClick={onDownload}>{t("Download from bSDD")}</Menu.Item>
    </Menu.Dropdown>
  );
}
