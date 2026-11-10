import { ActionIcon, Badge, Button, Group, Loader, Modal, Stack, Table, Text, Tooltip } from "@mantine/core";
import { IconDownload, IconHistory, IconPlus } from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api";
import { attempt, notifyOk } from "../notify";
import { op, useProject } from "../state/project";
import { useSettings } from "../state/settings";
import { hasUnsaved } from "../state/unsaved";
import { useUi } from "../state/ui";
import { askConfirm } from "./dialogs";

interface Snapshot {
  id: string;
  time: number;
  classes: number;
  properties: number;
  version?: string | null;
}

/** Saved versions of the dictionary (automatic backups + manual ones) with restore. */
export function VersionsDialog() {
  const { t } = useTranslation();
  const opened = useUi((s) => s.versions);
  const projectId = useProject((s) => s.projectId);
  const doc = useProject((s) => s.doc);
  const lang = useSettings((s) => s.language);
  const [list, setList] = useState<Snapshot[] | null>(null);
  const [max, setMax] = useState(20);
  const [busy, setBusy] = useState<string | null>(null);
  const close = () => useUi.getState().set({ versions: false });

  useEffect(() => {
    if (!opened || !projectId) return;
    setList(null);
    api<{ snapshots: Snapshot[]; max: number }>(`/api/projects/${projectId}/snapshots`)
      .then((r) => {
        setList(r.snapshots);
        setMax(r.max);
      })
      .catch(() => setList([]));
  }, [opened, projectId]);

  if (!opened || !projectId || !doc) return null;
  const fmt = new Intl.DateTimeFormat(lang === "de" ? "de-DE" : "en-GB", { dateStyle: "medium", timeStyle: "short" });
  const now = { classes: (doc.dictionary.Classes ?? []).length, properties: (doc.dictionary.Properties ?? []).length };
  const delta = (n: number, cur: number) => (n === cur ? null : <Text span size="xs" c={n > cur ? "teal" : "red"}> ({n > cur ? "+" : ""}{n - cur})</Text>);

  const saveNow = async () => {
    setBusy("new");
    const r = await attempt(() => api<{ snapshots: Snapshot[] }>(`/api/projects/${projectId}/snapshots`, { method: "POST" }));
    setBusy(null);
    if (r) {
      setList(r.snapshots);
      notifyOk(t("Version saved"));
    }
  };

  const restore = async (s: Snapshot) => {
    if (hasUnsaved()) {
      const go = await askConfirm(t("Unsaved changes"), t("You have unsaved edits in a form. Restoring a version replaces the dictionary; save or discard your edits first."), t("Restore anyway"), true);
      if (!go) return;
    }
    const ok = await askConfirm(
      t("Restore version"),
      t("Replace the current dictionary with the version from {{time}}? Everybody working on it gets this version. You can undo the restore with Ctrl+Z.", { time: fmt.format(s.time * 1000) }),
      t("Restore"),
    );
    if (!ok) return;
    setBusy(s.id);
    const done = await attempt(async () => {
      // keep the current state as a version too, then restore as one undoable operation
      await api(`/api/projects/${projectId}/snapshots`, { method: "POST" });
      const saved = await api<{ dictionary: unknown; extras: unknown }>(`/api/projects/${projectId}/snapshots/${s.id}`);
      await op("project.restore", saved);
      return true;
    });
    setBusy(null);
    if (done) {
      notifyOk(t("Version from {{time}} restored", { time: fmt.format(s.time * 1000) }));
      close();
    }
  };

  const download = async (s: Snapshot) => {
    const saved = await attempt(() => api<{ dictionary: unknown }>(`/api/projects/${projectId}/snapshots/${s.id}`));
    if (!saved) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(saved.dictionary, null, 1)], { type: "application/json" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: `${doc.dictionary.DictionaryCode}-${s.id}.json` });
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Modal opened onClose={close} title={<Group gap={8}><IconHistory size={18} />{t("Version history")}</Group>} size="lg">
      <Stack gap="sm">
        <Group justify="space-between" align="flex-start" wrap="nowrap">
          <Text size="sm" c="dimmed">
            {t("While the dictionary is edited, a version is saved automatically from time to time. The newest {{n}} versions are kept.", { n: max })}
          </Text>
          <Button variant="light" leftSection={<IconPlus size={14} />} onClick={saveNow} loading={busy === "new"} style={{ flex: "none" }}>{t("Save version now")}</Button>
        </Group>
        {!list ? (
          <Group justify="center" p="lg"><Loader size="sm" /></Group>
        ) : list.length === 0 ? (
          <Text c="dimmed" size="sm" ta="center" p="lg">{t("No saved versions yet.")}</Text>
        ) : (
          <Table verticalSpacing={6} highlightOnHover>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>{t("Saved")}</Table.Th>
                <Table.Th>{t("Version")}</Table.Th>
                <Table.Th>{t("Classes")}</Table.Th>
                <Table.Th>{t("Properties")}</Table.Th>
                <Table.Th />
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {list.map((s) => (
                <Table.Tr key={s.id}>
                  <Table.Td>{fmt.format(s.time * 1000)}</Table.Td>
                  <Table.Td>{s.version ? <Badge variant="light" color="gray" tt="none">v{s.version}</Badge> : null}</Table.Td>
                  <Table.Td>{s.classes}{delta(s.classes, now.classes)}</Table.Td>
                  <Table.Td>{s.properties}{delta(s.properties, now.properties)}</Table.Td>
                  <Table.Td>
                    <Group gap={4} justify="flex-end" wrap="nowrap">
                      <Tooltip label={t("Download this version as bSDD JSON")}>
                        <ActionIcon variant="subtle" color="gray" aria-label={t("Download this version as bSDD JSON")} onClick={() => download(s)}><IconDownload size={16} /></ActionIcon>
                      </Tooltip>
                      <Button size="compact-sm" variant="light" loading={busy === s.id} disabled={!!busy && busy !== s.id} onClick={() => restore(s)}>{t("Restore")}</Button>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
        <Text size="xs" c="dimmed">{t("Numbers in brackets: difference to the current dictionary.")}</Text>
      </Stack>
    </Modal>
  );
}
