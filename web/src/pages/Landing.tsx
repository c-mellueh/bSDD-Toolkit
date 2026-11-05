import { ActionIcon, Anchor, Badge, Button, Card, Container, FileButton, Grid, Group, Modal, SegmentedControl, Select, SimpleGrid, Stack, Text, TextInput, Title, Tooltip } from "@mantine/core";
import { modals } from "@mantine/modals";
import { IconCloudDownload, IconFilePlus, IconFileUpload, IconPackageImport, IconTrash } from "@tabler/icons-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { ApiError, api, readFileText } from "../api";
import { DownloadDialog } from "../components/DownloadDialog";
import { LanguageSelect } from "../components/LanguageSelect";
import { notifyError } from "../notify";
import { forgetProject, rememberProject, storageGet, useSettings, type RecentProject } from "../state/settings";

export function Landing() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [recent, setRecent] = useState(() => storageGet<RecentProject[]>("bsdd-recent", []));
  const [newOpen, setNewOpen] = useState(false);
  const [downloadOpen, setDownloadOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const open = (id: string, name: string) => {
    rememberProject(id, name);
    navigate(`/p/${id}`);
  };

  const upload = async (file: File | null, sloppy = false, text?: string) => {
    if (!file) return;
    setBusy(true);
    try {
      const content = text ?? (await readFileText(file));
      let data: Record<string, unknown>;
      try {
        data = JSON.parse(content);
      } catch {
        throw new Error(t("The file is not valid JSON"));
      }
      // project export (dictionary + editor data) or plain bSDD JSON
      const body = "dictionary" in data && "extras" in data ? { dictionary: data.dictionary, extras: data.extras, sloppy } : { dictionary: data, sloppy };
      const res = await api<{ id: string; meta: { name: string } }>("/api/projects", { method: "POST", json: body });
      open(res.id, res.meta.name ?? file.name);
    } catch (e) {
      if (e instanceof ApiError && e.status === 422 && e.body?.can_sloppy) {
        modals.openConfirmModal({
          title: t("The file contains invalid data"),
          children: (
            <Stack gap="xs">
              <Text size="sm">{e.message}</Text>
              <Text size="sm">{t("Do you want to load it anyway? Invalid parts will be removed.")}</Text>
            </Stack>
          ),
          labels: { confirm: t("Load anyway"), cancel: t("Cancel") },
          onConfirm: () => upload(file, true, text),
        });
      } else notifyError(e);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ height: "100%", overflow: "auto" }}>
      <Container size="md" py="xl">
        <Group justify="space-between" mb="xl">
          <Group gap="sm">
            <img src="/favicon.svg" width={36} height={36} alt="" />
            <div>
              <Title order={2}>bSDD Toolkit</Title>
              <Text c="dimmed" size="sm">{t("Create and edit buildingSMART Data Dictionaries together")}</Text>
            </div>
          </Group>
          <Group gap="xs">
            <LanguageSelect />
            <ThemeSwitch />
          </Group>
        </Group>

        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
          <ActionCard icon={<IconFilePlus />} title={t("New dictionary")} text={t("Start with an empty dictionary")} onClick={() => setNewOpen(true)} />
          <FileButton onChange={(f) => upload(f)} accept="application/json,.json">
            {(props) => <ActionCard {...props} icon={<IconFileUpload />} title={t("Open JSON file")} text={t("Upload a bSDD JSON file (or a project file)")} loading={busy} />}
          </FileButton>
          <ActionCard icon={<IconCloudDownload />} title={t("Download from bSDD")} text={t("Import a published dictionary from buildingSMART")} onClick={() => setDownloadOpen(true)} />
          <Card withBorder padding="md">
            <Group gap="sm" wrap="nowrap" align="flex-start">
              <IconPackageImport />
              <div>
                <Text fw={600}>{t("Shared links")}</Text>
                <Text size="sm" c="dimmed">{t("Every dictionary gets its own link. Everybody with the link can edit it at the same time.")}</Text>
              </div>
            </Group>
          </Card>
        </SimpleGrid>

        <Title order={4} mt="xl" mb="sm">{t("Recently opened")}</Title>
        {recent.length === 0 ? (
          <Text c="dimmed" size="sm">{t("No dictionaries opened in this browser yet.")}</Text>
        ) : (
          <Stack gap={4}>
            {recent.map((p) => (
              <Card key={p.id} withBorder padding="xs">
                <Group justify="space-between" wrap="nowrap">
                  <Anchor onClick={() => open(p.id, p.name)} style={{ minWidth: 0 }}>
                    <Text truncate fw={500}>{p.name}</Text>
                  </Anchor>
                  <Group gap="xs" wrap="nowrap">
                    <Badge variant="light" color="gray">{new Date(p.opened).toLocaleString()}</Badge>
                    <Tooltip label={t("Remove from list (the dictionary itself is kept)")}>
                      <ActionIcon variant="subtle" color="gray" onClick={() => { forgetProject(p.id); setRecent(storageGet("bsdd-recent", [])); }}>
                        <IconTrash size={16} />
                      </ActionIcon>
                    </Tooltip>
                  </Group>
                </Group>
              </Card>
            ))}
          </Stack>
        )}
      </Container>
      <NewDictionaryModal opened={newOpen} onClose={() => setNewOpen(false)} onCreated={open} />
      <DownloadDialog opened={downloadOpen} onClose={() => setDownloadOpen(false)} />
    </div>
  );
}

function ActionCard(props: { icon: React.ReactNode; title: string; text: string; onClick?: () => void; loading?: boolean }) {
  const { icon, title, text, onClick, loading } = props;
  return (
    <Card withBorder padding="md" style={{ cursor: "pointer", opacity: loading ? 0.6 : 1 }} onClick={onClick}>
      <Group gap="sm" wrap="nowrap" align="flex-start">
        {icon}
        <div>
          <Text fw={600}>{title}</Text>
          <Text size="sm" c="dimmed">{text}</Text>
        </div>
      </Group>
    </Card>
  );
}

export function ThemeSwitch() {
  const { t } = useTranslation();
  const theme = useSettings((s) => s.theme);
  const set = useSettings((s) => s.set);
  return (
    <SegmentedControl
      size="xs"
      value={theme}
      onChange={(v) => set({ theme: v as "auto" | "light" | "dark" })}
      data={[
        { value: "auto", label: t("Auto") },
        { value: "light", label: t("Light") },
        { value: "dark", label: t("Dark") },
      ]}
    />
  );
}

const LANGUAGES = ["en-GB", "en-US", "de-DE", "nl-NL", "fr-FR", "it-IT", "es-ES", "sv-SE", "nb-NO", "pl-PL", "da-DK", "fi-FI", "cs-CZ"];

function NewDictionaryModal({ opened, onClose, onCreated }: { opened: boolean; onClose: () => void; onCreated: (id: string, name: string) => void }) {
  const { t } = useTranslation();
  const [form, setForm] = useState({ DictionaryName: "", OrganizationCode: "", DictionaryCode: "", DictionaryVersion: "0.0.1", LanguageIsoCode: "de-DE" });
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [k]: e.currentTarget.value });
  const versionOk = /^(0|[1-9]\d*)(\.(0|[1-9]\d*)){0,2}$/.test(form.DictionaryVersion);
  const create = async () => {
    setBusy(true);
    try {
      const res = await api<{ id: string; meta: { name: string } }>("/api/projects", { method: "POST", json: { header: form } });
      onCreated(res.id, res.meta.name);
    } catch (e) {
      notifyError(e);
    } finally {
      setBusy(false);
    }
  };
  return (
    <Modal opened={opened} onClose={onClose} title={t("New dictionary")}>
      <Grid>
        <Grid.Col span={12}><TextInput label={t("Dictionary name")} value={form.DictionaryName} onChange={set("DictionaryName")} data-autofocus /></Grid.Col>
        <Grid.Col span={6}><TextInput label={t("Organization code")} value={form.OrganizationCode} onChange={set("OrganizationCode")} placeholder="default" /></Grid.Col>
        <Grid.Col span={6}><TextInput label={t("Dictionary code")} value={form.DictionaryCode} onChange={set("DictionaryCode")} placeholder="default" /></Grid.Col>
        <Grid.Col span={6}><TextInput label={t("Version")} value={form.DictionaryVersion} onChange={set("DictionaryVersion")} error={!versionOk && t("e.g. 1.0.0")} /></Grid.Col>
        <Grid.Col span={6}>
          <Select label={t("Language")} data={LANGUAGES} value={form.LanguageIsoCode} onChange={(v) => setForm({ ...form, LanguageIsoCode: v ?? "en-GB" })} searchable />
        </Grid.Col>
      </Grid>
      <Group justify="flex-end" mt="md">
        <Button variant="default" onClick={onClose}>{t("Cancel")}</Button>
        <Button onClick={create} loading={busy} disabled={!versionOk}>{t("Create")}</Button>
      </Group>
    </Modal>
  );
}
