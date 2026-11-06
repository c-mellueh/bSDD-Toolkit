import { Alert, Anchor, Badge, Button, Divider, FileButton, Group, List, Modal, Progress, Select, Stack, Text, TextInput } from "@mantine/core";
import { modals } from "@mantine/modals";
import { IconBolt, IconFileUpload, IconLogin, IconLogout } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { ApiError, api } from "../api";
import { currentSignIn, loginConfig, signIn, signOut, type BsddLoginConfig } from "../bsddAuth";
import { notifyError } from "../notify";
import { rememberProject } from "../state/settings";
import { useDictionaryUpload } from "./useDictionaryUpload";

interface Job {
  id: string;
  status: string;
  message: string;
  classes_done: number;
  classes_total: number;
  properties_done: number;
  properties_total: number;
  project_id: string | null;
  error: string | null;
}

interface RemoteDictionary {
  uri: string;
  name: string;
  version: string;
  organization: string;
  status: string;
}

export function DownloadDialog({ opened, onClose }: { opened: boolean; onClose: () => void }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [uri, setUri] = useState("");
  const [list, setList] = useState<RemoteDictionary[] | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const timer = useRef<number>();
  const [login, setLogin] = useState<BsddLoginConfig | null>(null);
  const [session, setSession] = useState(currentSignIn);
  const [fullBusy, setFullBusy] = useState(false);
  const { upload, busy: uploading } = useDictionaryUpload(onClose);

  useEffect(() => {
    if (!opened) return;
    void loginConfig().then(setLogin);
    setSession(currentSignIn());
  }, [opened]);

  useEffect(() => {
    if (!opened || list) return;
    api<{ dictionaries: RemoteDictionary[] }>("/api/bsdd/dictionaries")
      .then((r) => setList(r.dictionaries))
      .catch((e) => setListError(e.message));
  }, [opened, list]);

  useEffect(() => () => window.clearInterval(timer.current), []);

  // signed in: the complete dictionary as one file (like the bSDD website's download button)
  const startFull = async (sloppy = false) => {
    const token = currentSignIn();
    if (!token) {
      setSession(null);
      return start();
    }
    setFullBusy(true);
    try {
      const res = await api<{ id: string; meta: { name: string } }>("/api/download/full", {
        method: "POST",
        json: { uri, sloppy },
        headers: { "X-Bsdd-Token": token.access_token },
      });
      const item = list?.find((d) => d.uri === uri);
      rememberProject(res.id, item?.name ?? res.meta.name ?? uri);
      onClose();
      navigate(`/p/${res.id}`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        signOut();
        setSession(null);
      }
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
          onConfirm: () => startFull(true),
        });
      } else notifyError(e, t("Download dictionary from bSDD"));
    } finally {
      setFullBusy(false);
    }
  };

  const start = async () => {
    try {
      const j = await api<Job>("/api/download", { method: "POST", json: { uri } });
      setJob(j);
      timer.current = window.setInterval(async () => {
        const s = await api<Job>(`/api/download/${j.id}`);
        setJob(s);
        if (s.status !== "running") {
          window.clearInterval(timer.current);
          if (s.status === "done" && s.project_id) {
            const item = list?.find((d) => d.uri === uri);
            rememberProject(s.project_id, item?.name ?? uri);
            navigate(`/p/${s.project_id}`);
          }
        }
      }, 800);
    } catch (e) {
      setJob({ id: "", status: "error", message: "", classes_done: 0, classes_total: 0, properties_done: 0, properties_total: 0, project_id: null, error: (e as Error).message });
    }
  };

  const cancel = async () => {
    if (job?.id) await api(`/api/download/${job.id}`, { method: "DELETE" }).catch(() => undefined);
    window.clearInterval(timer.current);
    setJob(null);
  };

  const running = job?.status === "running" || fullBusy;
  const pct = (a: number, b: number) => (b ? Math.round((a / b) * 100) : 0);

  return (
    <Modal opened={opened} onClose={running ? () => undefined : onClose} title={t("Download dictionary from bSDD")} size="lg">
      <Stack>
        {login && (
          <Group justify="space-between" wrap="nowrap" className="bsdd-signin">
            {session ? (
              <>
                <Group gap={6} wrap="nowrap" style={{ minWidth: 0 }}>
                  <Badge color="green" variant="light" leftSection={<IconBolt size={12} />}>{t("Full download")}</Badge>
                  <Text size="sm" truncate>{t("Signed in as {{name}}", { name: session.name ?? t("buildingSMART user") })}</Text>
                </Group>
                <Button size="compact-sm" variant="subtle" color="gray" leftSection={<IconLogout size={14} />} disabled={running} onClick={() => { signOut(); setSession(null); }}>{t("Sign out")}</Button>
              </>
            ) : (
              <>
                <Text size="sm" c="dimmed">{t("Sign in with your buildingSMART account to download the complete dictionary in one step.")}</Text>
                <Button size="compact-sm" variant="light" leftSection={<IconLogin size={14} />} disabled={running} onClick={() => signIn().catch((e) => notifyError(e))}>{t("Sign in with buildingSMART")}</Button>
              </>
            )}
          </Group>
        )}
        <Select
          label={t("Published dictionaries")}
          placeholder={list ? t("Search…") : listError ? t("Could not load list") : t("Loading…")}
          searchable
          clearable
          disabled={running || !list}
          data={(list ?? []).map((d) => ({ value: d.uri, label: `${d.name} ${d.version} — ${d.organization ?? ""}` }))}
          value={list?.some((d) => d.uri === uri) ? uri : null}
          onChange={(v) => setUri(v ?? "")}
          limit={200}
        />
        <TextInput label={t("Dictionary URI")} value={uri} onChange={(e) => setUri(e.currentTarget.value)} disabled={running} placeholder="https://identifier.buildingsmart.org/uri/…" />
        {listError && <Text size="xs" c="dimmed">{listError}</Text>}
        {fullBusy && (
          <Stack gap={4}>
            <Text size="sm">{t("Downloading the complete dictionary…")}</Text>
            <Progress value={100} animated />
          </Stack>
        )}
        {job && (
          <Stack gap={4}>
            <Text size="sm">{t(job.message)}</Text>
            <Text size="xs">{t("Classes")} {job.classes_done}/{job.classes_total}</Text>
            <Progress value={pct(job.classes_done, job.classes_total)} animated={running} />
            <Text size="xs">{t("Properties")} {job.properties_done}/{job.properties_total}</Text>
            <Progress value={pct(job.properties_done, job.properties_total)} animated={running} />
            {job.error && <Alert color="red">{job.error}</Alert>}
          </Stack>
        )}
        <Group justify="flex-end">
          {running ? (
            <Button color="red" variant="light" onClick={cancel}>{t("Cancel")}</Button>
          ) : (
            <>
              <Button variant="default" onClick={onClose}>{t("Close")}</Button>
              <Button onClick={() => (session ? startFull() : start())} disabled={!uri}>{t("Download")}</Button>
            </>
          )}
        </Group>
        <Divider label={t("or")} labelPosition="center" />
        <Stack gap={6}>
          <Text size="sm" fw={600}>{t("Open a file downloaded from bSDD")}</Text>
          <List size="sm" type="ordered" spacing={2}>
            <List.Item>
              {t("Open the dictionary on")}{" "}
              <Anchor href="https://search.bsdd.buildingsmart.org" target="_blank" rel="noopener noreferrer">search.bsdd.buildingsmart.org</Anchor>{" "}
              {t("and click “Download” (requires a buildingSMART account).")}
            </List.Item>
            <List.Item>{t("Choose the downloaded JSON file here.")}</List.Item>
          </List>
          <Group>
            <FileButton onChange={(f) => upload(f)} accept="application/json,.json">
              {(props) => <Button {...props} variant="default" leftSection={<IconFileUpload size={14} />} loading={uploading} disabled={running}>{t("Open bSDD JSON file…")}</Button>}
            </FileButton>
          </Group>
        </Stack>
      </Stack>
    </Modal>
  );
}
